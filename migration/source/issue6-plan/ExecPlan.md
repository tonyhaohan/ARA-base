---
status: active
owner: core-maintainers
last_verified: 2026-07-11
scope: Issue #6 配置驱动的 RDMA QP 绑定与 bridge 侧 QP 分组
code_paths: docs/simulator/astra_ns3/QP_CONFIGURATION_REQUIREMENTS.md, src/mcnf_sim_bridge/interfaces/astra_ns3_schedule.py, scripts/generate_qp_bindings.py, scripts/run_manual_astra_smoke.py, tests/test_qp_bindings.py, repos/astra-sim/astra-sim/network_frontend/ns3/
---

# 实现最小、可信的 QP 配置与分组接口

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. This plan follows `docs/guideline/PLAN.md`.

## Purpose / Big Picture

Issue #6 要让 bridge 用少量、明确的 RDMA QP 表达 solver 的路径分配。用户可以定义由具体 physical edge 组成的完整最短路径、QP、QP group 和 flow-to-group；bridge 按 4096B message 哈希一次选择 QP，ASTRA ns-3 frontend 只读取已经解析的配置并复用 persistent QP。完成后，含平行链路的多级网络可以显式利用全部完整路径，而不是生成 100+ QP 等待逐跳哈希近似均衡。

可观察结果是 bundle 新增 simulator ABI `qp_config.json` 以及审计文件 `qp_assignments.csv`、`qp_children.json`；真实 ASTRA `fct.txt`/trace 中的 QP、字节数和每一跳具体 interface 与配置一致。同一 QP 的连续 message 保持 alias、source port、sequence space 和拥塞控制对象。关闭功能时，现有标准 smoke 行为不变。

## User Raw Prompts

- “我记得当时我们的探索好像走进了弯路。现在的问题在于实现过于复杂，QP 安排的过多，但基本功能和能力尚未达标。

  例如，当前 QP 分配采用哈希绑定，即每个 QP 的路径由哈希随机决定，而非按顺序逐一绑定。这导致需在每条路径上绑定 100+ QP 才能实现相对均衡。

  但我期望的是“逐包哈希”，而非“逐 QP 哈希”。即按顺序给每条路径放置一个或少量几个 QP，再将 4KB 小包均匀分布在这些 QP 上（可通过哈希或均匀 spray 实现均衡）。

  请确认：
  1. 现在的情况是否符合我说的？
  2. 该功能仿真器是否天然支持？”

- “在的仿真器是否支持通过读取某些配置文件来手动指定 QP 的绑定公式？如果是这样的话，我们可以自己写一个脚本来生成这些绑定，从而间接支持。另外在不同 QPS 之间均匀分配，或者用哈希做近似均匀分配的功能，生成器到底有了吗？具体是怎样的方式？另外请你记下来，最好写在项目的 agents.md 里面：我们这个项目模拟的是深度学习GPU集群里面的通信过程，所以我们的仿真器应当以 RDMA 为设计基础。”

- “你认为：移植 SimAI 的 QP-reuse/message-queue 逻辑到现有 ns-3 adapter，再把编译期常量改成配置项，这个修改会带来多大的变化，大概多少行代码？是否涉及仿真器核心逻辑的更改？安全性如何？我希望这个改动尽可能小且安全。因为我们这个实验的目的是给出一个我们自己求解器可信的证明，因此我们用的仿真器必须是可信的，而且是大家公认可信的。如果我们过多地调整了仿真器，大家就会不信任我们，而且我们自己也有可能会出错。

  但是我认为这个功能其实应该是非常简单的。因为它本质上就是去手动设定一些 QP，而非只能用自动的哈希来生成。这个功能甚至会比哈希自动生成还要简单才对。

  你帮我评估一下这个修改的复杂度和安全性。”

- “给我讲讲什么叫做 QP reuse？难道不是我们只指定了一下QP怎么绑吗？难道是每次发完一个大任务之后，qp 就会被注销，然后在下一个任务的时候再重新构造吗？真实网络行为是这样的吗？如果是这样的话，我们的仿真功能当然要与真实网络行为保持一致。另外，首先我认为读取配置文件来构造 QP 的方法是对我们最合适的。此外，我还希望它支持一个功能，就是对不同的 QP 去做分组，并且我可以指定分组。因为后面可能会遇到这样的情况，比如说两个 GPU 之间有 5 条不同的物理路径，然后我会指定其中 3 条上面均匀地发送一部分任务，另外 2 条上面均匀地发送一部分任务，这样就是涉及到流量在 QP 之间均匀分配。我希望能够给每个流量都指定一组 QP。你认为这个功能是否可行？对应的修改是否安全？”

- “仿真器只做最小修改，支持从配置文件读取 QP 配置即可；生成这些 QP 配置文件的逻辑放在接口代码里。”

- “很好，你整理一下我们的需求，整理出来一篇文档并开一个新的issue。是不是可以丢掉现在分支的工作内容了？”

- “你先在这个分支上面快速实现一下，我预期对仿真器代码的修改可以控制在 50 行以内。另外你可以单独写一个生成 QP 绑定关系的脚本，这个脚本我估计在 200 行以内即可。分支应当是从 main checkout 出来的，而不是从 issue3 出来的。”

- “实现完后，快速测试几个关键 case，评估仿真效果与理论预期的差距，并分析这条路是否走得通。”

- “非常好，跑一下我们n、m、p架构下的实验，在这里面，同一个起点和终点的所有 QP 都放在同一组。并且每条路径分别测试放一个 QP、两个 QP、四个 QP 会有什么不同。

  你先把那个网格粗略扫一遍，不要每个都扫，完整实验太慢了，汇报一下初步结果。”

- “你是不是没搞明白我们的 n、m、q 参数系统啊？你看看 issue3 里面我的规定，这一套 class 实验系统会是我们以后非常重要的基准实验。”

- “好的，那你粗粗的扫一下这个表格吧，我想要一个 In general 的结论。”

- “这个实验的相关代码要固化下来，我们以后会经常跑这个实验。你可以参考 Issue 3 里面这个实验的代码。”

- “非常好！commit push，然后分别给主仓库和仿真器仓库提PR。”

- “多级网络的指定完整路径这个我们需要：比如两个GPU到一个交换机都有两条链路，那么两个GPU之间就有四条路径，这四条我们需要都能利用上，尽管他们一定被分到一个等价组里。
  任意非最短 solver path是什么意思？我经常需要自己定义出来从a卡到b卡允许走哪些路径，他们未必全是跳数最少的路径。
  逐包 spray、adaptive routing是什么意思？我理解的是，这个是已经建立好QP之后在QP上的发送过程，而我们改源码是为了安排QP？所以这个功能不需要改源码？”

- “根本不需要考虑我们现在已经实现了什么。我们现在其实实现的是对一个 Toy Model 的初步测试，后面完全可以把它改掉重新实现。然后我们取消对于非最短路径的支持吧，因为实际上我们现在的算法也都是只选了票数最短的路径来跑的。2.1你理解的没问题。2.2 反向ACK等完全无所谓，怎么简单怎么来。2.3可以加仿真前检测，仿真器本身保持简洁。感觉现在我们的难点在于，我们试图在一开始就绑定好完整的 QP 路径，但是实际上网络行为是 greedy 的，是到了某一个节点之后去查这个节点的下一跳的表的，我理解的对吗？

  那如果是这样的话，我们怎样确保信息的发送确实是按照我们预定义的 QP 来进行的呢？

  请仔细思考这部分的机理，并且告诉我每一部分涉及到哪一层代码的修改。”

- “那你看看我们还有未澄清的部分吗？如果没有了，就给我列一个完整的修改计划。如果必须要改那个 ns3 代码库，那你就直接把它加入到我们现在 Astra sim MCNF 的那个代码库里面，不要再新建一个代码库了。”

- “好，开始执行。你那个建议如果不涉及ns3代码修改就可以改。我希望最终我们对 ns3 部分的修改能控制在 30 行以内，对整个仿真器模块所做的修改尽可能控制在 150 行以内，尽可能把所有修改都放在我们bridge接口代码里面。这些代码行数约束并不是硬约束，你不要为了它而牺牲一些功能或者把代码写得很混乱。但是如果最后超了，你要向我汇报超了多少以及为什么超了。”

- “走closeout流程。另外：以后我在让你完整计划某个修改的时候，或者我让你理解我的意思的时候，都要按照之前说的框架来说，但我针对性提问的时候不必，这个事情写入AGENTS.md.：
  用户明确要求，在后续回复中不要把用户需求与代理建议混在一起。涉及需求分析、设计或实现评估时，按以下三部分分别表达，并逐条说明对应修改：

  1. `我理解的用户需求`：只复述用户已经提出的硬需求，使用双方都能理解的术语，不加入建议。
  2. `为形成完整功能仍需澄清或补充的部分`：只列用户尚未明确、存在歧义或实现完整功能必须定义的契约，并说明每项会涉及什么修改。
  3. `额外建议或锦上添花`：只列非必需的代理建议，明确标注可选，并说明每项会涉及什么修改。

  如果某部分没有内容，明确写“无”，不要把其他部分的内容移入。技术讨论优先回看项目 ExecPlan 中的 `User Raw Prompts`，以用户原始表述恢复需求边界。”

## Progress

- [x] (2026-07-10 18:41 CST) 审计 Issue #3、旧分支、当前 ASTRA/ns-3 QP 生命周期和真实 NCCL QP 语义。
- [x] (2026-07-10 18:41 CST) 创建 GitHub Issue #6 和关联分支 `codex/6-qp-config-groups`。
- [x] (2026-07-10 18:41 CST) 写出需求文档 `docs/simulator/astra_ns3/QP_CONFIGURATION_REQUIREMENTS.md`。
- [x] (2026-07-10 21:20 CST) 在 200 行的 `scripts/generate_qp_bindings.py` 实现 QP、group、flow-to-group、4096B round-robin lowering、bundle 守恒校验和原版 Murmur3 source-port preimage 搜索。
- [x] (2026-07-10 21:20 CST) 生成 `qp_bindings.csv`、`qp_assignments.csv`、`qp_children.json` 并把 child schedule 写回 bundle metadata。
- [x] (2026-07-10 21:32 CST) 在 ASTRA ns-3 frontend 增加 default-off、strict binding reader。
- [x] (2026-07-10 21:45 CST) 完成 feature-off smoke、K=1/2/3/5、五路径 3+2、原生 packet trace 和错误尺寸 fail-fast 验收。
- [x] (2026-07-10 22:20 CST) 增加 topology fingerprint 与 trace-backed route manifest，逐项校验 `(src,dst,routeSlot) -> expectedPath`，并用交换 slot/path 和错误 topology 负例证明 fail-fast。
- [x] (2026-07-10 22:43 CST) 粗扫 `(N,M)=(2,1),(2,4),(8,4),(16,4)` 共 12 个 Q=1 diagnostic case；后续确认该结果只是 N/M/Q 基准的子切片，不是完整粗网格。
- [x] (2026-07-10 23:02 CST) 重读 Issue #3 的用户原始规定，恢复 N=GPU、M=switch、Q=每个 GPU-switch pair 平行物理链路数的完整基准契约。
- [x] (2026-07-10 23:08 CST) 让 Q>1 的同邻居平行 interface 成为可绑定的 RDMA route entry，并对不支持的 Q>1 `LINK_DOWN` fail-fast；未改 RDMA/Qbb/CC/switch hash 数据面。
- [x] (2026-07-10 23:32 CST) 固化 `scripts/run_clos_qp_benchmark.py`，支持完整网格、增量 case、R=1/2/4、双哈希端口、trace 校准、JSON/CSV 和标准 N×M 报告。
- [x] (2026-07-10 23:47 CST) 粗扫 9 个代表 topology × 3 个 R；27/27 成功并完整重跑，给出 in-general 结论。
- [ ] 在独立未修改 binary 上补做 Q=1/无重复邻居的 feature-off byte/FCT parity，并为论文归档补全 build flags 与 Linux 正式环境结果。
- [ ] 经用户审查后决定 Issue #3 关闭和旧远端分支删除时间。
- [x] (2026-07-11 00:26 CST) 创建 nested ns-3 PR `astra-sim/astra-network-ns3#20` 与依赖它的 ASTRA simulator Draft PR `tonyhaohan/astra-sim-mcnf#1`。
- [x] (2026-07-11 20:00 CST) 更新现有 ASTRA 与 bridge Draft PR，并明确合并顺序为 ASTRA 在前、bridge 在后。
- [x] (2026-07-11 18:54 CST) 按最终需求重新打开设计：完整路径以具体物理 edge 表示，只支持跳数最短路径，4KB message 只在选择 QP 时哈希一次，ACK/CNP 保持原生行为。
- [x] (2026-07-11 19:22 CST) 验证“路径专属目的 IP 别名 + 单出口路由项”能固定含平行链路的完整 data path；Q=2 四条组合路径的 8 个有向 QP 全部通过 native trace。
- [x] (2026-07-11 19:24 CST) 实现 persistent QP FIFO，并用同一 alias/source-port 的两个连续 1MiB message 验证 sequence 延续。
- [x] (2026-07-11 19:27 CST) 用新设计替换 source-port preimage Toy Model；43 个 Python tests 通过，且 vendoring 前同一 adapter/ns-3 行为补丁的 C++ target build 通过。
- [x] (2026-07-11 19:29 CST) 完成四个代表 topology × R=1/2/4 的 12-case 粗扫；全部成功，理论差距 3.83%--9.37%，R 最大影响 0.79%。
- [x] (2026-07-11 20:13 CST) 将用户指定的需求/澄清/建议三段式回复契约写入项目 `AGENTS.md`，并明确针对性提问不强制套用。
- [x] (2026-07-11 21:48 CST) 完成自审；两个 PR 均无 CI/reviewer 输出。用普通 merge 合并 ASTRA PR #1，父仓 gitlink 更新到 ASTRA `main` merge commit `181c785`。

## Surprises & Discoveries

- Observation: 当前 ASTRA frontend 每个 `sim_send` 创建一个新 QP，最后 ACK 后删除发送和接收 QP。
  Evidence: `repos/astra-sim/astra-sim/network_frontend/ns3/entry.h::send_flow()` 与 `qp_finish()`，以及 nested ns-3 `RdmaHw::QpComplete()`。

- Observation: 真实 verbs/NCCL 通常在连接或 communicator 生命周期中复用 QP；配置相同 source port 重新创建 QP 不等于 persistent reuse。
  Evidence: NVIDIA RDMA programming manual 和 NCCL `net_ib` create/post/close 源码。

- Observation: Issue #3 的 qphash custom collective 可以并发发出多个 RDMA QP；剩余问题不是所有 send 被 rank 完全串行化。
  Evidence: 旧分支 `2026-07-03_issue3_custom_collective_concurrency_audit.yaml` 和源码调用链审计。

- Observation: 旧分支相对 `main` 有 67 个独有提交、61 个文件和约 9252 行新增，混入校准估计、lane-expanded proxy、high-K QP 搜索和 Ara 机制。
  Evidence: `git diff --stat main...origin/codex/3-clos-alltoall-calibration`。

- Observation: 多条连接到同一个邻居的平行边不一定成为不同 route entry；第一版只能承诺 binding 到 backend 可区分的 next-hop。
  Evidence: Issue #3 single-layer route audit。

- Observation: 2 GPU、5 switch 的 K=1/2/3/5 实测完成时间为 172.069/87.078/58.775/36.116 us，相对 K=1 加速为 1.000/1.976/2.928/4.764x；每条 child 都从 0 ns 启动。
  Evidence: `runs/issue6_qp_binding_key_cases/*/output/fct.txt`。

- Observation: 五路径 3+2 case 恰好生成五条 2 MiB child，整体 44.582 us，相对纯 payload 下界高 6.29%，相对 ns-3 standalone 低 0.03%。
  Evidence: `runs/issue6_qp_binding_key_cases/groups_3_plus_2/output/fct.txt`。

- Observation: 原生 packet trace 将 source ports 10006/10003/10002/10005/10000 映射到 host 0 interfaces 1/2/3/4/5，即本次 build 中的物理路径 `0-2-1` 到 `0-6-1`。
  Evidence: `runs/issue6_qp_binding_key_cases/groups_3_plus_2_trace/output/mix.tr`。

- Observation: routing vector 来源于 `map<Ptr<Node>, ...>` 遍历和 vector push order，因此 hash slot 到具名路径的映射需要每个 topology/build 用 trace manifest 验证，不能作为跨平台稳定 ABI。
  Evidence: nested ns-3 `scratch/common.h::CalculateRoute()` 与 `SetRoutingEntries()`。

- Observation: 当前 pinned ASTRA 的 macOS build 在 stdout/stderr 不是终端时会在启动前退出；`script -q` 或 lldb 分配伪终端后同一二进制稳定完成。这是本地旧依赖/日志栈的运行环境问题，不是 QP binding 路径错误。
  Evidence: direct subprocess return `-11`，同一参数经 `script -q` exit 0；Linux 正式环境仍应单独复跑。

- Observation: 初次只检查 active port 的实现允许同一 source port 在前后 message 中复用，但旧 QP 的完成回调早于 core QP 删除，可能让后继 QP 被旧删除路径误删。
  Evidence: `entry.h::qp_finish()` 与 nested ns-3 `RdmaHw::QpComplete()` 调用顺序；最终 frontend 已改为读取配置时拒绝 run 内重复 `(src,dst,sourcePort)`。

- Observation: 初次 `apply_to_bundle()` 没有核对 child 与原 logical flow，错误 plan 可造成 `flows.csv` 与 ET/schedule 字节不一致。
  Evidence: review counterexample 8192B flow/4096B child；最终实现已校验 flow 集合、端点、task、phase、tag、port 和字节守恒，并增加负例测试。

- Observation: Q>1 有两次独立选择：host RDMA hash 选择 M*Q source interface，switch ECMP hash 再选择 Q 个 destination interface；只约束第一式会严重失衡。
  Evidence: `RdmaHw::GetNicIdxOfQp()`、`SwitchNode::GetOutDev()` 和 N=8/M=4/Q=2 的端口穷举。

- Observation: 双哈希 preimage 可把 routeSlot=m*Q+q 固定为 identity q→q 完整 data path；标准最坏 N=32/M=16/Q=4/R=4 的全部 endpoint 在 16-bit port 范围内有解。
  Evidence: `scripts/run_clos_qp_benchmark.py::_allocate_ports()` 与 exhaustive audit。

- Observation: slot-major group order 会把整 packet 余数聚集到前几个 path，R=4/MQ=16 时路径聚合差可达 3.23%；replica-major order 把上界收紧到 4096B。
  Evidence: `tests/test_clos_qp_benchmark.py::test_replica_major_members_balance_tail_bytes_across_physical_paths()`。

- Observation: 最终 27 case 粗网格中，相对 R=1 的最大绝对变化为 1.17%；N/M/Q 的容量缩放近似理论，且相同 M*Q 的不同分解在 R=1 下最大只差 0.20%。
  Evidence: `docs/plans/issue6_qp_config_groups/qp_per_path_coarse_results.md` 与 `runs/clos_qp_benchmark_coarse/summary.csv`。

- Observation: 复用通过 SHA 校验的 calibration cache 后，27 个正式 case 完整复跑的 `sim_us` 逐纳秒相同，FCT 行数和总字节一致；重建 binary 后 raw trace SHA 可变，但解析后的 interface mapping 不变。
  Evidence: `/tmp/clos_qp_benchmark_coarse_first.json`、`/tmp/clos_qp_before_crlf_rebuild.json` 与最终 `summary.json` 对比。

- Observation: 当前 host RDMA 和 switch 的转发表都以 destination IP 为键，并仅在该键对应多个出口时执行哈希。
  Evidence: nested ns-3 `RdmaHw::GetNicIdxOfQp()` 与 `SwitchNode::GetOutDev()`。因此 adapter 可以为每条预定义路径分配独立 destination alias，并在路径每一跳为该 alias 只注册一个出口；这条方案尚需真实 trace 验证。

- Observation: SimAI 当前公开实现的 `_QPS_PER_CONNECTION_` 是一次 `SendFlow` 拆成多个临时 QP，不是跨 message 保存 PSN/ACK/CC 状态的 persistent QP reuse。
  Evidence: `aliyun/SimAI` 当前 `astra-sim-alibabacloud/astra-sim/network_frontend/ns3/entry.h::SendFlow()` 仍为每个分片安装新的 `RdmaClientHelper`。

## Decision Log

- Decision: 新实现从干净 `main` 开始，不 merge 或整体 cherry-pick Issue #3 分支。
  Rationale: 旧分支已经把多条探索路线和历史产物混在一起，不符合最小可信补丁边界。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): simulator 只读取最小 `qp_bindings.csv`，所有 group、均分、tag 和 source-port 搜索都由 bridge 完成。
  Rationale: 这使 simulator patch 局限在 frontend 输入层，保留原版 RDMA/ECMP/CC 数据面。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): bridge 把一个 logical flow 展开成每个非空 QP share 一条 child send，而不是在 simulator 内部 fan-out。
  Rationale: custom collective 已验证可发出并发 QP；在 interface 完成展开可以保持 simulator callback 契约最小，并让每条 child 有唯一 tag 和独立 FCT 证据。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): 第一版只支持 4096B 等权确定性分配。
  Rationale: 用户的当前证明目标需要准确均衡；weighted、adaptive 和随机 hash allocation 都不是完成当前能力所必需。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): 第一版不实现 persistent QP reuse。
  Rationale: 当前用户要求 simulator 只做配置读取；真实 reuse 会改变 QP 生命周期、ACK/sequence/CC 状态，应作为独立功能审计。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): 快速原型只接受 single-phase schedule；multi-phase 输入直接失败。
  Rationale: ASTRA 的 phase barrier 会额外产生 1-byte send；在未定义它们的绑定和 logical-flow join 语义前，拒绝输入比静默漏配或错误依赖更安全。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): simulator 接受的是 source-port binding，不接受 `path_id`；具名 solver path 通过原生 trace manifest 验证。
  Rationale: 保持原版 RDMA hash、route selection 和 packet data plane，避免把求解器结论硬注入仿真核心。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): V1 source port 在一次 run 内全局唯一，不做顺序复用。
  Rationale: 当前 backend 的完成回调与 QP 删除顺序不能安全承载相同 key 的立即复用；真正 reuse 必须连同 message queue 和 QP 生命周期另行实现。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): 多路径 plan 必须携带 topology fingerprint、trace fingerprint 和显式 route-slot manifest。
  Rationale: backend route vector 的指针遍历顺序不是稳定 ABI；只验证“路径存在”不能证明某个 hash slot 对应 solver 指定的具名路径。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): 首轮 diagnostic 把 Q 固定为 1，用 M 个 switch 表示可绑定路径。
  Rationale: 当时 backend 只保留同一邻居最后一个 interface；该 12-case 结果只保留为 Q=1 子切片，不再作为标准粗网格。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): 标准实验恢复 Issue #3 的完整 N/M/Q，并增加独立维度 R=每条 identity q→q 完整物理路径 QP 数。
  Rationale: N/M/Q 是长期 class benchmark；Q>1 通过最小 parallel route-entry fix、双哈希 preimage 和 native trace 接口核对成为真实可绑定容量。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): simulator patch 限定为 48 additions/9 deletions；Q>1 parallel-link expansion 是 correctness fix，不声称与错误的 upstream Q>1 feature-off 行为 parity。
  Rationale: 保持 RDMA/Qbb/CC/switch hash core 不变，同时诚实区分 Q=1 parity 与 Q>1 修复。
  Date/Author: 2026-07-10 / Codex local

- Decision (superseded): N/M/Q/R group 使用 replica-major/slot-minor member order，正式 case 必须是 maxR trace calibration plan 的精确 QP 子集。
  Rationale: 消除 tail-packet 顺序对 R 对比的路径负载污染，并闭合配置、trace 与性能 case 的证据链。
  Date/Author: 2026-07-10 / Codex local

- Decision: 完整路径使用 path-specific destination alias 编译为逐跳单出口 route；ns-3 固定快照直接 vendoring 到私有 ASTRA 仓库。
  Rationale: 该方案复用原版按目的地址查表的数据面，每个 alias 只有一个 next hop，能够把 solver 的完整 edge path 直接编译成逐跳路由项；nested ns-3 只承担 persistent QP 生命周期，避免新增 QP-aware switch lookup。用户要求必要的 ns-3 修改直接纳入私有 ASTRA 仓库，不再维护第三个仓库。
  Date/Author: 2026-07-11 / Codex local

- Decision: source-port preimage 与 route-slot manifest 方案标记为 superseded，保留旧结果只作为 Toy Model 诊断证据。
  Rationale: 它依赖两个原生哈希的偶然 preimage，不能作为复杂多级网络中“QP 明确绑定完整物理路径”的稳定接口。
  Date/Author: 2026-07-11 / Codex local

- Decision: 配置 QP 在 message 完成后保持对象、5-tuple、sequence 和 CC 状态；同 QP 的 send 使用 FIFO。
  Rationale: 这与真实连接级 QP reuse 一致，也避免把相同 `qpId` 仅当作审计标签。nested ns-3 只需一个 persistent flag 和完成分支，数据包生成、ACK、PFC 与 CC 算法不变。
  Date/Author: 2026-07-11 / Codex local

## Outcomes & Retrospective

最终设计已替换 Toy Model。bridge plan 直接用 physical edge id 定义完整路径，验证连续性、endpoint 和最短 hop；4096B message 只在 group 内选择 QP 时哈希一次。adapter 把完整路径编译成 path-specific destination alias 的逐跳单出口 route，原版 host/switch hash 因候选集大小为 1 而不会改变路径。

配置 QP 已实现 persistent reuse。同一 QP 的并发 child send 进入 FIFO；message 完成后延长已有 QP sequence，不更换 alias 或 source port，并保留 CC 对象。双 message smoke 的两段 1MiB FCT 都是 23.333us，第二段从第一段完成时开始，总 wall time 46.666us。

Q=2 四条组合路径的 8 个有向 QP 全部通过 native trace。新 12-case N/M/Q/R 粗扫全部成功，理论差距 3.83%--9.37%，R=2/4 相对 R=1 最大变化 0.79%，PFC event 为 0。默认 R=1 仍成立。Python suite 为 `43 passed`。vendoring 前，同一 adapter 与 ns-3 行为补丁的 `AstraSimNetwork` target build 通过并产出了上述真实 trace；将固定 ns-3 快照直接导入私有 ASTRA 仓库后，clean build 已越过本次修改的 ns-3 模块，但在 pinned ASTRA 自带的旧 fmt/spdlog 与当前 AppleClang 的 `consteval` 兼容错误处停止。该工具链问题与本次 QP 数据面修改无关，未为绕过它扩大补丁。

实现、行数审计和自审已完成；ASTRA PR #1 已用普通 merge 合入，bridge gitlink 指向其 `main` merge commit `181c785`。bridge PR #7 合并后 Issue #6 可由 `Closes #6` 自动关闭。论文级 Linux clean build/复跑作为后续归档任务。packet spray、adaptive routing、failure reroute、非最短路径和 multi-phase 仍明确不在本次范围。

旧 Issue #3 分支的 high-K 实现路线可以退出，但暂不删除。它仍是诊断证据入口，也包含已关闭 Issue #4 的 Ara 合并记录。待 Issue #6 完成独立 upstream parity、必要结论已落在主线文档后，再关闭 #3 并删除旧分支最安全。

## Context and Orientation

`scripts/generate_qp_bindings.py` 是 bridge 侧 lowering。输入 plan 用 physical topology 的 edge id 定义完整路径，再定义 QP、group 和 logical flow。脚本在仿真前验证 edge 连续性、endpoint、最短 hop、group endpoint、端口和字节守恒，生成 `qp_config.json`、`qp_assignments.csv` 和 `qp_children.json`。`src/mcnf_sim_bridge/interfaces/astra_ns3_schedule.py` 只负责把这些 child send 写成现有 ASTRA schedule/Chakra ET，不再包含 QP 路由搜索。

`qp_config.json` 是唯一 simulator ABI。每条 resolved QP 包含 source/destination rank、source port、path-specific destination alias；每条 route 指定 `(destination alias, node, physical interface)` 的唯一出口；每条 message binding 把一个 schedule send 映射到 QP。simulator 不读取 group，也不运行 solver。

ASTRA adapter 在启动时安装 alias route，并按 `(src,dst,tag,size)` 消费 message binding。同一 QP 的 send 进入 FIFO。nested ns-3 的 persistent flag 让完成的配置 QP 保持活跃，并在后续 message 到来时扩展 sequence space；未配置 QP 仍按上游行为销毁。

## Plan of Work

第一阶段在 bridge 中解析并验证 edge-level shortest paths、QP、group 和 flow。4096B message 以 BLAKE2s 对 `(seed, flow id, message index)` 哈希一次选择 group member，同一 flow/QP 的 message 聚合成一个 child send。round-robin 只用于 trace calibration，保证每个配置 QP 至少出现一个 4096B message。

第二阶段在 adapter 中读取 resolved JSON、分配 path-specific destination alias、逐跳安装单出口 route、严格匹配 child send，并按 QP 排队。原版 destination lookup 看到单一候选，因此 host/switch hash 无法改变配置路径。

第三阶段在 nested ns-3 只增加 persistent QP 生命周期分支，不修改 packet format、switch forwarding、RDMA data generation、ACK/NACK/CNP、PFC、ECN 或 congestion-control 算法。为避免单体仓库的循环链接，`seq-ts-header.cc` 的编译归属从 applications 移到其实际消费者 point-to-point。

第四阶段用 Python 单测、四条平行完整路径 trace、双 message reuse smoke 和 N/M/Q/R 粗网格验证。Linux clean build/复跑保留为 paper-grade 归档门槛。

## Concrete Steps

从 issue worktree `/private/tmp/mcnf-sim-bridge-issue6` 工作。基础验证：

    PYTHONPATH=src pytest -q

生成配置并跑标准 smoke：

    PYTHONPATH=src python scripts/run_manual_astra_smoke.py \
      --suite minimal --limit 1 --force \
      --qp-plan /absolute/path/to/qp_plan.json

验证同一 QP 连续 message：

    PYTHONPATH=src python scripts/run_qp_reuse_smoke.py

长期 N/M/Q/R 基准入口：

    PYTHONPATH=src python scripts/run_clos_qp_benchmark.py \
      --case 2,1,1 --case 2,1,2 --case 4,2,1 --case 4,2,2 \
      --r-values 1,2,4 --run-astra \
      --protobuf-lib-dir "$CONDA_PREFIX/lib"

检查 `qp_config.json`、`qp_assignments.csv`、`qp_children.json`、`schedule.csv`、`output/fct.txt` 和 native packet trace，而不只看退出码。

## Validation and Acceptance

自动测试覆盖合法 3+2 分组、message hash 可复现、round-robin calibration、tail message、空组、endpoint 不一致、重复 path/QP/group、非法端口、未知 edge、edge 不连续、非最短路径、alias 编码范围、child tag 范围和字节守恒。

真实 Q=2 trace 必须逐 QP 核对 source interface、switch ingress、switch egress 和 destination interface，证明四个 incoming/outgoing lane 组合都可用。reuse smoke 必须观察到两个 message 使用同一 alias/source port 且第二段从第一段完成时开始。N/M/Q/R 粗网格必须核对总字节、FCT、PFC event 和理论带宽差距。

关闭配置时不得安装 alias route或启用 persistent lifecycle。nested ns-3 行为改动目标不超过 30 changed lines；ASTRA adapter/frontend additions 目标不超过 150 行。vendored upstream snapshot 的基线文件不计入行为补丁行数，但必须记录 commit、LICENSE 和来源。

## Idempotence and Recovery

固定 plan 与 topology 应生成 byte-identical resolved config 和审计文件。invalid plan 必须在启动 simulator 前失败。运行产物留在 ignored `runs/`，不提交大体积 trace/FCT。

不修改用户 main worktree 中未提交的 `AGENTS.md`。不向公共 ns-3 仓库提交 PR；ns-3 固定快照直接由私有 `astra-sim-mcnf` 管理。旧 Issue #3 分支在 Issue #6 验收前只读保留，不执行 reset、force delete 或覆盖式 checkout。

## Artifacts and Notes

- GitHub issue: <https://github.com/tonyhaohan/mcnf-sim-bridge/issues/6>
- Requirements: `docs/simulator/astra_ns3/QP_CONFIGURATION_REQUIREMENTS.md`
- Simulator input: `qp_config.json`
- Audit artifacts: `qp_assignments.csv`, `qp_children.json`
- Reuse smoke: `scripts/run_qp_reuse_smoke.py`
- Coarse QP/path results: `docs/plans/issue6_qp_config_groups/qp_per_path_coarse_results.md`
- Durable benchmark: `scripts/run_clos_qp_benchmark.py`
- Vendored ns-3 provenance: `repos/astra-sim/extern/network_backend/ns-3/UPSTREAM.md`
- Historical evidence: Issue #3 comments and `origin/codex/3-clos-alltoall-calibration`

## Interfaces and Dependencies

Bridge generator 只使用 Python 标准库，不引入新依赖。plan schema version 为 2，packet size 固定 4096B。adapter 使用仓库已存在的 nlohmann JSON 读取 `qp_config.json`，唯一新增启动接口为可选 `--qp-config-file`。

ns-3 固定在 upstream commit `f764bed27630ee45368c03e22e4f952b69fab30a`。行为补丁仅涉及 persistent flag/completion branch 和 `seq-ts-header.cc` 的 CMake 编译归属；ASTRA adapter 是本功能的主要实现层。

Revision note 2026-07-10 / Codex local: created this plan after replacing the high-K QP hash exploration with an explicit, configuration-driven QP binding and bridge-side grouping design.

Revision note 2026-07-11 / Codex local: superseded the source-port-preimage Toy Model with edge-level shortest paths, destination aliases, persistent QP FIFO, Q² parallel-path enumeration, trace/reuse smoke validation, and the canonical N/M/Q/R benchmark. Vendored the pinned ns-3 snapshot into the private ASTRA repository and recorded exact behavior-patch budgets and the remaining AppleClang compatibility limitation.
