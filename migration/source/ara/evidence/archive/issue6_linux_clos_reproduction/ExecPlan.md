---
status: archived
owner: codex-local
last_verified: 2026-09-15
scope: Issue 6/9 的原始 Linux 代表案例复现计划；2026-09-16 仅补文档元数据，正文保留历史状态
---

# 在 Linux 服务器复现单层 Clos 代表案例


本文件依照 `docs/guideline/PLAN.md` 维护，接续 Issue #6/#9 已记录的 Linux 复跑工作，不新建研究图。只新增实验记录，不修改仿真器、求解器或 bridge 行为。工作分支为 `codex/6-linux-clos-reproduction`，本轮不自动提交、推送或创建 PR。

## Purpose / Big Picture


用户希望先在新租服务器上复现师兄已有的单层 Clos 场景，再考虑把仿真时间相对理想带宽时间的差距缩小到 5%～8%。本轮优先回答能否复现，不能通过修改物理参数去保证某个百分比。已有 1 MiB 两卡例子只证明环境可用，不等于本轮 8 MB 性能复现。

## User Raw Prompts


“师兄说：我们bridge那个仓库里之前做过一些事情，你可以先看看，里面我应该设置了单层clos的实验，里面记录了基本的实验的设置，我记得之前做的最重要的一个修改就是改了QP的绑定方式，从自动hash绑定变成按顺序均匀绑定，现在单层clos大概都到10%以内了，我感觉目标是5%-8%吧，你先看看我当时的分析。”

“所以我们目前的主要目标就是先把师兄弄好了的场景（也就是单层CLOS，对吧？我们刚刚做的这个例子，调整数据量和带宽，能不能得到差不多的结果？），在咱们租的服务器上给他复现出来，对吧”

用户随后授权开始执行。先完成最小例子，再完成其余三个代表拓扑，比较旧 hash 和当前 round_robin；不扩大到五卡多层 Allreduce、完整求解器或全标准网格。

## Progress


- [x] 2026-09-15：阅读 Issue #6/#9 执行计划、标准实验、原始记录、全局 ARA 图和规范；确认本地与远端 main 均为 `1d4f816`。
- [x] 2026-09-15：确认服务器首次编译和 1 MiB 复跑已通过，ASTRA 为 `181c785`，70 项自动测试通过。
- [x] 2026-09-15：创建独立本地实验记录分支，明确只复现四个拓扑的 R=1 切片。
- [x] 2026-09-15：第一批16次运行完成，两卡为166.208微秒；但发现同目录强制重跑校准覆盖旧trace，不能作为完整正式归档。
- [x] 2026-09-15 19:11：按每遍、每策略独立目录重新运行全部16次，保留第一批作为记录失败的证据。
- [x] 2026-09-15：验收0错误，16份校准共520次QP路径复核、8组配对配置核验通过，实际ELF哈希独立重算一致；全部复跑逐纳秒一致。
- [x] 2026-09-15：完成历史对照和中文报告；正式hash历史最大差0.1843%，均匀分配gap为3.88%～6.39875%，保留根因未定边界。
- [x] 2026-09-15：添加 ARA 负结果、输出隔离转向、复现与配对实验节点、证据及session。
- [x] 2026-09-15：生成全局图，ARA校验36节点/54边/33证据/12claims/5sessions通过；包含本轮记录的Linux隔离快照70项测试全部通过（1.81秒）。
- [x] 2026-09-15：独立审阅数字与结论边界通过；最后的记录专项19项测试与diff检查通过。

## Context and Orientation


服务器是 Ubuntu 22.04、16 vCPU、32 GiB，公网地址 `116.205.103.45`。已安装的工作区为 `/home/mcnfsim/mcnf-smoke`，普通用户 `mcnfsim` 执行模拟。bridge 在该目录的 `mcnf-sim-bridge`，ASTRA 在其 `repos/astra-sim`，Python 在 `server-smoke-kit/.venv-linux/bin/python`。首次安装细节位于本地工作区外层 `outputs/server_bootstrap_20260915/INSTALLATION_RECORD.md`。

N 为卡数，M 为并行交换机数，Q 为每对卡—交换机的平行物理链路数，R 为每条完整物理路径的 QP 数。QP 是绑定到一条物理路径的发送通道。本轮使用 `(N,M,Q)=(2,1,1),(2,1,2),(4,2,1),(4,2,2)`，全部 R=1。每张卡向其他每张卡各发送 8,000,000 字节，这是十进制 8 MB，不是 8 MiB。每条链路 400 Gbps、传播延迟 500 ns、小包 4096 字节；理论时间为 `160*(N-1)/(M*Q)` 微秒。保持现有拥塞控制、ACK 和路径配置机制不变。

两种策略均先明确绑定完整路径，区别仅在小包选择哪个 QP：hash 是确定性哈希近似均衡，round_robin 是依序轮流分配。旧 `docs/plans/issue6_qp_config_groups/qp_per_path_coarse_results.md` 的 8 MB 性能结果为 hash；当时的校准使用 round_robin，不能把校准策略误标成正式策略。旧 R=1 四个时间为 166.208、86.909、255.585、131.249 微秒，文档精度为 0.001 微秒。

## Plan of Work / Milestones


第一阶段只调用既有 `scripts/run_clos_qp_benchmark.py`，先测最小 8 MB 配置，再测其他三个拓扑。所有参数显式给出，源版本和工作树先检查；每条命令最长 300 秒，最多使用 CPU 0-7，顺序执行，不同时堆积仿真进程。

第二阶段对八种配置进行完全相同的复跑，用 first/hash、first/round_robin、repeat/hash、repeat/round_robin 四个目录隔离，不覆盖旧 1 MiB 结果。每个策略和每遍保留自己的完整校准证据；runner 已提供源码/二进制校验，继续沿用。

第三阶段取回原始结果，独立核对 summary 与 FCT、两种策略的 QP/路径定义及 rank 完成记录。比较历史 hash、Linux hash、Linux round_robin 三列，明确复现偏差与理论差距是两种指标。将新证据续接现有 Issue #6/#9 的全局图和 Q001 Linux 归档问题，不把 R=1 四拓扑结果外推到全部 12 案例或 225 个标准组合。

## Concrete Steps


本地包装脚本为 `D:/codex/集合通信仿真26暑/outputs/clos_reproduction_20260915/run_reproduction.sh`，复制到服务器 `/home/mcnfsim/mcnf-smoke/run_clos_reproduction_20260915.sh`。先 `bash -n` 检查，再经 root 登录执行：

    runuser -u mcnfsim -- bash /home/mcnfsim/mcnf-smoke/run_clos_reproduction_20260915.sh

脚本会新建 `experiments/clos_reproduction_20260915_XXXXXX` 目录，输出 `EXPERIMENT_ROOT`。包装脚本在每次运行中采用：

    PYTHONPATH=<bridge>/src <venv>/bin/python scripts/run_clos_qp_benchmark.py \
      --case 2,1,1 --r-values 1 --size-bytes 8000000 \
      --message-allocation hash --run-astra --force \
      --run-root <experiment>/first/hash --astra-root <bridge>/repos/astra-sim \
      --protobuf-lib-dir /usr/lib/x86_64-linux-gnu

其他拓扑、策略与 repeat 由包装脚本依次调用；每遍每策略 summary 应有 4 行，共 16 次性能运行。最后输出 `REPRODUCTION_EXECUTION_OK` 仅表示运行完成，还必须通过独立验收。

## Validation and Acceptance


每行必须 status=success，数据量和 R 正确，FCT 条数等于实际承载数据的 QP 数，累计字节为 `N*(N-1)*8,000,000`，每张卡都完成。理论公式独立复算，仿真时间不能低于该配置的理想带宽时间；round_robin 的每逻辑流小包数差不超过 1。记录但不隐藏任何丢包、PFC 或 stderr 异常。

各策略配对必须拥有相同二进制、物理拓扑、QP 与路径组，只允许小包分配不同。路径证据来自独立真实校准而非正式性能案例的全包轨迹。first 与 repeat 的 sim_us 应逐纳秒一致；历史值只精确到 0.001 微秒，不能声称更精细的历史复现。5%～8% 是后续优化目标，不是本轮伪造成功或忽略高差距案例的条件。

本地实验分析工具放在 `outputs/clos_reproduction_20260915/analyze_reproduction.py`，运行后生成对照报告。归档后执行 `PYTHONPATH=src python scripts/validate_ara.py`、`python scripts/render_ara_graph.py` 及全套 pytest，要求全部通过。

## Surprises & Discoveries


已知历史“3.83%～9.37%”来自 8 MB/hash 的 12 案例；当前 1 MiB/round_robin 的两卡结果 23.648 微秒与历史同规格一致，不能因数据量不同直接判为复现失败。

第一批 `clos_reproduction_20260915_dXbRHT` 数值复跑一致，但同一个 run-root 先后用 --force 执行 hash 与 round_robin，会重写 calibration。首遍两卡 hash 行引用 trace SHA `b59ac902...`，目录留下的却是 rr 的 `134f6823...`。`_calibrate()` 在 force=True 时重建并覆盖，而旧汇总行保留原 SHA。这个目录不能证明所有行的原始校准 trace 仍可重算；完整保留，不修改旧 summary 或伪造哈希。只调整包装脚本输出目录后重新执行。

新增研究节点后，本地旧 test_ara.py 将节点数和session数写死为32/4，已仅同步为36/5。Windows全套测试另有一个既有macOS环境模拟测试因Windows盘符冒号而失败；不修改该无关测试或运行时代码。改用服务器新建的隔离记录快照验证，70项全部通过；用于真实仿真的原服务器源码仍保持干净。

## Decision Log


2026-09-15：接续既有 Issue #6/#9 Linux 复跑问题，使用含 #6 编号的独立记录分支，不创建或修改外部 Issue/PR。

2026-09-15：保留旧 hash 为真正历史对照，同时测试当前 round_robin。先固定 R=1，因为原分析未发现增加 R 的稳定容量收益；本轮不全扫 225 个组合。

2026-09-15：服务端保持已编译的干净固定源码；本地分支只写执行计划和研究归档，避免记录变化影响实际使用的源码或缓存。

2026-09-15：遇到校准证据覆盖后，分配策略也成为目录边界。旧批次作为负结果保留；不修改核心runner，也不放松校验或把旧trace指纹替换成新值。

2026-09-15：只更新ARA快照计数断言以匹配新增记录，不改变仿真测试逻辑。Linux记录快照由固定HEAD的git archive加本轮记录覆盖层组成，在新临时目录运行，不覆盖实际实验代码。Windows跨平台路径测试问题保留为环境限制，不在本任务扩展修复。

## Idempotence and Recovery


每次运行用 mktemp 创建新目录；脚本失败时保留所有输出，不递归删除。重跑整个包装脚本会生成新的证据目录。各命令只在本次新建目录使用 `--force`，不触碰旧实验。连接失败时先检查既有 SSH 白名单，不擅自开放所有来源，不修改系统或付费配置。

## Artifacts and Notes


本地准备和结果目录为 `D:/codex/集合通信仿真26暑/outputs/clos_reproduction_20260915`。正式批次为其中的 `clos_reproduction_20260915_cd9hTY`，对应服务器 `/home/mcnfsim/mcnf-smoke/experiments/clos_reproduction_20260915_cd9hTY`。完整记录包含原始first/repeat四个策略目录、comparison.json/.md、native_path_audit.json、console.log与provenance.txt；失败批次dXbRHT完整保留。私钥保持在本机，不写入实验产物。

本地验收命令（D:/python/python.exe 是本机 Python）为：

    D:/python/python.exe -B outputs/clos_reproduction_20260915/analyze_reproduction.py <本地正式批次目录>
    D:/python/python.exe -B outputs/clos_reproduction_20260915/verify_native_paths.py <本地正式批次目录> <本地bridge目录>

前者生成 PASS、0 errors，并保留8条跨运行trace原始哈希不同的提示；后者重新解析全部16份trace并输出520次QP路径验证成功。每份trace与自身引用均匹配，跨运行原始字节不同不冒充逐字节相同。实际服务器二进制独立sha256sum为 `7f9db19d50dafbe8d371c9f64cbef8b9e7b27cb7794fb1c62e6be8956ade67f4`。

## Interfaces and Dependencies


复用既有 ASTRA/ns-3 runner、Python 虚拟环境、已编译二进制和校准解析代码，不安装新依赖。新增分析工具只读原始产物并生成报告，不回写仿真输入。本轮只增加包装脚本与研究记录，不改变仿真接口。

## Outcomes & Retrospective


既定的四个R=1代表拓扑已经完成运行和完整证据验收。hash四值为166.208/86.826/255.114/131.030us，均匀分配为166.208/85.119/249.999/127.660us，两遍一致。当前均匀分配四例均低于8%，这是限定配置的测量结论，不代表所有单层Clos或五卡Allreduce。最小例与历史表一致，其余hash微差原因未定，不宣称全部逐纳秒历史复现。

研究图接续 I006-N11～N13、I009-N11，保留了校准覆盖的失败尝试及未定位历史微差。Q001完整Linux归档仍open，原12案例的R=2/4和225全网格尚未补齐。本轮结构、记录图和Linux全套70项自动测试均已通过，既定复现工作完成；未提交、推送或修改远端Issue/PR。

最终Linux测试快照为服务器正式批次内 `record_audit_MK3iYU`，其原始validation.log已取回外层outputs的 `linux_record_validation.log`。它验证了包含本轮ARA和计数断言更新的代码快照，而非只重跑旧记录版本。

更新说明：2026-09-15，记录首批归档失败、独立目录复跑、完整验收、历史差异与有限覆盖结论；不修改物理或协议参数。
