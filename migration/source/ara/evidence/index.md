---
status: active
owner: core-maintainers
last_verified: 2026-09-17
scope: mcnf-sim-bridge 项目级 ARA evidence index
---

# Evidence Index

Evidence id 使用 `E<issue>-<sequence>`。大运行产物留在 ignored `runs/`；这里保存其路径、命令、关键数字和解释。

## Issue #3

### E003-01：原始 Clos N/M/Q 目标

What it proves: 用户要求用真实网络行为验证 N/M/Q Clos all-to-all，并保留正的固定开销和包切分尾部效应。

Artifact: GitHub Issue #3；`origin/codex/3-clos-alltoall-calibration` 上的 `docs/plans/issue3_clos_alltoall_calibration/ExecPlan.md`。

Evidence type: requirement.

### E003-02：Bridge 侧校准估计

What it proves: 解析估计可以直接拟合目标公式，但不能证明真实 ASTRA/ns-3 使用了指定物理路径。

Artifact: Issue #3 历史报告和 commit `356e5de`。

Evidence type: baseline with credibility limit.

### E003-03：Raw-rank solverPath 失败

What it proves: bundle 中拆分 solverPath 不会让真实 ASTRA raw rank 自动获得 M/Q 并行注入，也不是 simulator 路由契约。

Artifact: Issue #3 raw-rank probe；Issue #3 progress comment。

Key numbers: `N=2,M=2,Q=1` 为 165.172us vs 80.036us；`N=2,M=1,Q=2` 为 166.135us vs 80.036us。

Evidence type: negative.

### E003-04：Lane-expanded proxy 的价值与边界

What it proves: 把每条 lane 展开成独立 ASTRA rank 可以展示 M/Q 容量，但改变了原始 GPU rank 语义。

Artifact: Issue #3 lane-expanded runs、历史报告和 ExecPlan。

Key numbers: 最大运行到 2048 ASTRA ranks；大量大 N case 达标，小 N 高并行度 case 仍受固定开销影响。

Evidence type: partial positive.

### E003-05：Native all-to-all 失败

What it proves: ASTRA native direct/ring 等 collective 没有为同一 GPU pair 提供要求的 M/Q 路径利用率。

Artifact: Issue #3 native all-to-all probes 和历史报告。

Key numbers: direct `N=8,M=2,Q=1` 为 982.526us vs 560.000us；ring `N=8,M=1,Q=1` 为 4654.114us vs 1120.000us。

Evidence type: negative.

### E003-06：High-K QP hash striping

What it proves: 大量 QP 可以通过 backend hash 改善部分 case，但 K 与结果非单调、需要高 QP 数且不能形成明确路径契约。

Artifact: Issue #3 `qphash` probes、历史报告和 branch commits。

Key numbers: 部分 case 需要 K=64、120、134 甚至更高；邻近 K 可能退化。

Evidence type: mixed.

### E003-07：ECMP-visible topology

What it proves: 把平行链路改写成不同 next-hop 可以让 Q 参与 hash，但仍然不能指定完整物理路径或稳定满足所有 case。

Artifact: Issue #3 `qphash+ecmptopo` probes 和历史报告。

Key numbers: `N=2,M=2,Q=2,K=16` 从 96.860us 改善到 53.148us；多个小 N case 仍高于目标。

Evidence type: mixed.

### E003-08：Backend 参数与 hash 控制面搜索

What it proves: queue、CC、rendezvous、delay、source-port、ECMP seed 和进一步 K 搜索没有把 high-K proxy 变成通用方案。

Artifact: Issue #3 历史 ExecPlan observations；branch head `7cde3ed`。

Evidence type: negative.

### E003-09：Issue #3 到 Issue #6 的转向

What it proves: 用户明确拒绝依赖 100+ QP 的随机哈希近似，要求少量 QP、完整路径绑定和每个逻辑流可指定的 QP组；Issue #6 据此替换 Toy Model。

Artifact: Issue #6 opening rationale、`docs/plans/issue6_qp_config_groups/ExecPlan.md` 和最终 merge chain。

Evidence type: user-revised pivot.

## Issue #6

### E006-01：用户需求与可信性边界

What it proves: 用户要求少量明确的 QP组、每个 QP 绑定一条完整物理路径、4KB小包只选择一次 QP，并把 simulator 修改保持最小。

Artifact: `docs/plans/issue6_qp_config_groups/ExecPlan.md` 的 `User Raw Prompts`；GitHub Issue #6。

Evidence type: requirement.

### E006-02：High-K 自动哈希是死路

What it proves: 生成 100+ QP 并等待自动哈希近似均衡复杂且间接，不能表达要求的路径组和 QP组。

Artifact: Issue #6 opening rationale 和 ExecPlan 中的 Issue #3 audit。

Evidence type: negative.

### E006-03：Source-port preimage prototype

What it proves: source-port 搜索可以命中 backend hash slot，五路径 3+2 case 也能分配字节，但 route-slot 顺序依赖 build，不能作为稳定完整路径 ABI。

Artifact: `runs/issue6_qp_binding_key_cases/`；Issue #6 ExecPlan observations。

Key numbers: K=1/2/3/5 仿真时间 172.069/87.078/58.775/36.116us；五路径 3+2 为 44.582us。

Evidence type: mixed.

### E006-04：Q=2 四条完整物理路径

What it proves: path-specific destination alias 和逐跳单出口路由固定了两条平行入链路与两条平行出链路的四种组合。

Artifact: `docs/simulator/astra_ns3/QP_CONFIGURATION_REQUIREMENTS.md`；Issue #6 native trace validation。

Key numbers: 四条路径、八个有向 QP 全部匹配预期 interface。

Evidence type: positive.

### E006-05：Persistent QP reuse

What it proves: 同一 alias/source port 上两个连续 1MiB message 共享 persistent QP 并延续 sequence state。

Artifact: `scripts/run_qp_reuse_smoke.py`；Issue #6 closeout evidence。

Evidence type: positive.

### E006-06：N/M/Q/R 粗扫

What it proves: 每条完整路径的 QP 数从 R=1 增至 R=2/4 没有稳定容量收益。

Artifact: `docs/plans/issue6_qp_config_groups/qp_per_path_coarse_results.md`；`runs/clos_qp_benchmark_coarse/`。

Key numbers: 12/12 final representative cases；理论gap 3.83%--9.37%；最大 R-vs-R1 差异 0.79%；PFC 为 0。

Evidence type: positive with residual gap.

### E006-07：外部 ns-3 PR 是错误的 ownership boundary

What it proves: 项目不拥有公共 `astra-network-ns3` 仓库，错误 PR 被撤回，修改最终保留在私有 ASTRA 仓库。

Artifact: Issue #6 correction comment；closed PR `astra-sim/astra-network-ns3#20`。

Evidence type: negative process evidence.

### E006-08：最终修改规模与 merge chain

What it proves: 最终实现集中在 ASTRA适配层，并以最小 nested ns-3 修改通过自有仓库合并。

Artifact: ASTRA `181c785`；bridge `06bee4e`；Issue #6 closeout comment。

Key numbers: nested ns-3 21 changed lines；ASTRA adapter/frontend 150 additions。

Evidence type: positive.

### E006-09：最终验证

What it proves: code、bundle、trace、QP复用和 benchmark 在 closeout 前全部通过。

Artifact: Issue #6 closeout comment 和 ExecPlan progress。

Key numbers: 43 Python tests；7/7 bundle smoke；Q=2 complete-path trace；persistent-QP smoke；12/12 coarse sweep。

Evidence type: validation.

## Issue #14

### E014-01：用户选择方案一并保留方案二为开放问题

What it proves: 用户确认先保持正向均分、补齐普通回程并保留原生哈希；ACK 逐包轮询仅作为后续待验证方向。

Artifact: `docs/plans/issue14_clos_return_routes/ExecPlan.md` 的 User Raw Prompts；https://github.com/tonyhaohan/mcnf-sim-bridge/issues/14 。Issue 正文是对用户选择的记录，不是新性能证据。

Evidence type: user requirement and workflow decision.

### E014-02：正式集成与回归契约

What it proves: 本次限定输入、构建和运行配置边界，并保留原版对照；只说明正在执行的验证契约，不证明仿真已通过。

Artifact: `docs/plans/issue14_clos_return_routes/ExecPlan.md`；GitHub Development 关联分支 `codex/14-clos-return-routes`。

Key numbers: 开发前 Windows 基线 68 passed、1 skipped、1 failed；唯一失败是既有 Darwin 环境变量测试在 Windows 盘符上的冒号分割假设。新正式仿真尚未运行。

Evidence type: implementation contract and pre-change test observation, not performance validation.

### E014-03：当前实际构建身份与正式回归前置核验

What it proves: 本次在服务器上只读核验实际 ELF、ASTRA commit 与缓存 manifest 中的全部 18 项运行库；身份匹配为启用回程补全的前置条件，不单独证明性能回归通过。

Artifact: 外层 `outputs/clos_return_routes_20260916/preflight.json`、`validated_binary_manifest.json`、`existing_input_comparison.json`。实际二进制 SHA256 为 `7f9db19d50dafbe8d371c9f64cbef8b9e7b27cb7794fb1c62e6be8956ade67f4`，ASTRA commit 为 `181c7856ed77bac3be68495e2400752488df5e5a`；完整库映射规范 JSON SHA256 为 `e59f1150a2d2dea54daeeef9aa55224489004c50ae16457b65ac2a5a775bb3c7`，manifest 原始文件 SHA256 为 `5e3039743801dabf2549e994244b633a83afd3ff58a2292dd71ae9ff299cc68c`。

Key numbers: 2026-09-16 17:04 读取当前 manifest；服务器实际 `_valid_cache` 返回 true，ASTRA tracked 工作树干净。四个原候选的正式生成结果完全一致，新增路由数 384/256/0/2048，正向 children/assignments 未变。本条记录时新正式仿真尚未运行；历史 Issue 9 没有独立归档这份库映射，不能倒写成当时已完成的证明。

Evidence type: live read-only build validation and offline input equivalence; formal paired performance/trace validation pending.

后续闭环：本条保留初次核验时点的边界。当前实际构建已在 E014-05 的新正式回归中重新验证；不回填到历史 Issue 9。

### E014-04：实现审查、真实缓存及原入口兼容性

What it proves: 正式 bridge 实现保持 legacy/Q1，限制未支持输入；真实缓存能复用，篡改临时副本不能借自报哈希混入。Windows 既有失败没有被隐去。

Artifact: `docs/plans/issue14_clos_return_routes/RESULTS.md`；外层 `outputs/clos_return_routes_20260916`，正式服务器批 `issue14-return-routes-20260916-46Aon8` 的 `logs/linux_tests.log`、`meta/cache_runtime_check.json`、`results/manual_smoke_audit.json`。

Key numbers: Linux 176 passed、1 skipped；Windows 175 passed、1 skipped、同一既有路径分隔符测试失败。16 份真实缓存命中，3 项临时篡改反例拒绝，88 个原文件哈希不变。原有 7 个最小 smoke 实际运行与审计通过，90 条 FCT、219152384B。

Evidence type: independent code review, unit tests, live-cache tests and original-entry real-simulator smoke.

### E014-05：正式单层回归与完整证据审计

What it proves: 当前受限实现复现候选收益，原版与 Q1 没有改变；25 条配对场景的两遍结果一致，未遗漏失败或计划行。该计数包含两条跨批重复参数，对应 23 组唯一参数。

Artifact: `docs/plans/issue14_clos_return_routes/RESULTS.md`、`report_summary.json`、`html/index.html`；外层 `outputs/clos_return_routes_20260916/issue14-return-routes-20260916-46Aon8/results/audit.json`，SHA256 `2843ede7cf4119e7c2fca567bf838783a0f0826c32bd389504dd800674eebcb1`。取回归档 `issue14-evidence.tar.gz` SHA256 `cbf74adac398fe8390cc1018f7c69e78f5841532d0f6b1160562eef1f157b746`；完整 mix.tr 留在同名服务器任务目录。

Key numbers: 100/100 性能、179656 FCT、84 份校准/147400 QP 路径、4 份完整性能轨迹全部 PASS。8MB/R1 的 15 配置补全差距 2.99750%～6.29125%。8/2/4、8/4/2、8/2/1、32/2/2 补全时间精确复现 147292/147006/579554/1280798ns。Q1 的 7 配对严格不变，Q>1 的 18 配对均更快。32/2/2 每遍 PFC 记录 312→0，但未隔离 PFC 单独时间贡献。

Evidence type: controlled paired repeated integration regression, independently reconstructed inputs, raw completion/FCT/native-route audits and actual build fingerprints; not hardware or solver-Allreduce validation.

### E014-06：4MB 仍超 8% 与非单调 R 敏感性

What it proves: 补全不是消除一切残差；不能把 8MB 的达标推广到所有数据量，也不能把更多 QP 当作必然加速。

Artifact: 同批 `results/sensitivity` 和 `sensitivity_audit.json`，完整数表见正式报告。

Key numbers: 4MB 8/2/4 从 78171ns/11.67286% 降到 76008ns/8.58286%，仍超过 8%。8MB 8/2/4 补全 R1/R2/R4 分别 147292/147506/148621ns；8/4/2 分别 147006/146938/147336ns。每一行均两遍完全相同；未开展开销消融或方案二实现。

Evidence type: bounded sensitivity result and preserved target exception; causal residual decomposition remains open.

### E006-10：共享目录强制校准覆盖的负结果

What it proves: 相同 run-root 逐策略 --force 会重写校准证据，性能值一致不代表旧行的原始trace仍被保留。

Artifact: `ara/evidence/archive/issue6_linux_clos_reproduction/RESULTS.md`；本地外层 `outputs/clos_reproduction_20260915/clos_reproduction_20260915_dXbRHT/comparison.json` 与完整原始产物。

Key numbers: 16 次性能运行数值一致，但验收返回1并准确检测8条 hash 行 trace SHA 引用不匹配。原批次未删除、未篡改。

Evidence type: negative archive-integrity evidence.

### E006-11：分策略隔离后的 Linux 复现与原始证据验收

What it proves: 四个 R=1/hash 8 MB 案例可近似复现，固定环境重复结果一致，独立 trace 解析和参数配对通过。

Artifact: `ara/evidence/archive/issue6_linux_clos_reproduction/RESULTS.md` 和 ExecPlan；正式服务器 `/home/mcnfsim/mcnf-smoke/experiments/clos_reproduction_20260915_cd9hTY`；本地外层 `outputs/clos_reproduction_20260915/clos_reproduction_20260915_cd9hTY/` 下 comparison.json、native_path_audit.json、console.log、provenance.txt 及全部 first/repeat 原始产物。工具位于外层 `outputs/clos_reproduction_20260915/`。

Key numbers: 16次正式运行，0条验收错误，520条QP完成记录与520次校准路径复核、8组策略输入配对；hash四时间166.208/86.826/255.114/131.030us，历史最大偏差0.1843%。ELF SHA256为 `7f9db19d50dafbe8d371c9f64cbef8b9e7b27cb7794fb1c62e6be8956ade67f4`，服务器独立重算一致。校准原始哈希跨运行可不同，但逐份匹配且路径语义通过。

Evidence type: partial cross-build reproduction and positive scoped validation; historical microdifference remains unexplained.

Validation: 包含新增记录的Linux隔离快照 `record_audit_MK3iYU` 全套70项测试通过（1.81秒）；原始日志在外层 `outputs/clos_reproduction_20260915/linux_record_validation.log`。ARA校验36 nodes、54 edges、33 evidence、12 claims、5 sessions。

### E006-12：扩规模外层检查字段错误与独立重跑

What it proves: 仿真成功不代表外层执行检查正确；必须使用实际summary字段，失败批不冒充完整实验。

Artifact: 工作区外层 `outputs/clos_scaling_20260916/clos_scaling_20260916_core_86J6hV/console.log` 与该目录原始run_scaling.sh；`ara/evidence/archive/issue6_linux_clos_scaling/ExecPlan.md`。

Key numbers: 首个8/2/1性能案例完成后误读size_bytes触发KeyError；正确字段size_bytes_per_pair。只修正包装脚本，重新执行为正式core_8QrZpA批，不改核心源码或原产物。

Evidence type: retained wrapper failure and recovery provenance.

### E006-13：近期两次失败的独立恢复核验

What it proves: dXbRHT归档失败和core_86J6hV外层检查失败均已被同输入成功重跑覆盖，并非网络配置仍无法运行。

Artifact: 外层 `outputs/clos_diagnosis_20260916/failure_recovery.md`；对应9/15失败/成功批和9/16失败/核心成功批的原始wrapper、console、summary、FCT及校准文件。

Key numbers: 9/15旧批16次仿真成功但8条hash校准引用失配；隔离目录后的16条引用均匹配，80个关键输入/FCT文件与旧批逐字节相同。9/16首例579554ns，检查size_bytes触发KeyError；修正size_bytes_per_pair后12次成功，首例5个关键文件相同。原失败证据完整保留。

Evidence type: independent negative-result recovery audit; no new claim about historical rejected designs or unrun grid points.

## Issue #9

### E009-01：1MiB allocation 问题

What it proves: 用户要求真实比较均匀分配和哈希分配，并且只有均匀分配稳定时才修改默认值。

Artifact: GitHub Issue #9；`docs/plans/issue9_round_robin_default/ExecPlan.md`。

Evidence type: requirement.

### E009-02：配对真实 allocation 结果

What it proves: 12 组 topology/R 配对在两种 policy 下都成功，字节、FCT 守恒且 PFC 为 0。

Artifact: `docs/plans/issue9_round_robin_default/allocation_comparison.md`；`runs/issue9_1mib_allocation_compare/`。

Key numbers: 24 次真实 run；均匀分配相对 hash 平均 -5.02%，范围 0.00% 到 -8.90%，没有 case 变慢。

Evidence type: positive.

### E009-03：Hash imbalance 与 active QPs

What it proves: 哈希分配不是严格均衡，并可能让配置 QP 未承载小包。

Artifact: allocation comparison 和 Issue #9 ExecPlan discoveries。

Key numbers: hash 最大 QP小包数差值 32；`(4,2,2,4)` 使用 382/384 QPs；均匀分配使用 384/384 且差值 0。

Evidence type: comparative.

### E009-04：默认值与 legacy 语义

What it proves: `round_robin` 成为 missing-field 和 benchmark 默认值，显式 hash 保留，旧 row 仍按 hash 解释。

Artifact: commit `b84a64e`；allocator 和 benchmark tests。

Evidence type: decision and validation.

### E009-05：SHA-addressed build requirement

What it proves: 编译产物名需要 ASTRA short SHA，匹配时复用，不匹配时重建。

Artifact: Issue #9 ExecPlan `User Raw Prompts`；`docs/simulator/astra_ns3/STANDARD_EXPERIMENTS.md`。

Evidence type: requirement.

### E009-06：只缓存 executable 或 ns-3 libraries 不完整

What it proves: binary 动态链接 mutable runtime libraries；遗漏 protobuf 或优先加载外部 protobuf 会破坏 ABI provenance。

Artifact: PR #10 reviews；commits `b259571`、`016d25d`。

Evidence type: negative review evidence.

### E009-07：最终 cache manifest

What it proves: schema 2 保存完整 ASTRA SHA、platform、architecture、binary SHA256 和每个 ns-3/protobuf library SHA256；dirty tree 被拒绝。

Artifact: `scripts/astra_ns3_binary.py`；`tests/test_astra_ns3_binary.py`。

Evidence type: positive.

### E009-08：真实 cache reuse

What it proves: 不完整旧 cache 自动失效并重建，verified binary 和 libraries 随后完成真实 ASTRA case。

Artifact: Issue #9 ExecPlan 和 closeout comment。

Key numbers: 1MiB `(N,M,Q,R)=(2,1,1,1)` case 重复得到 23.648us。

Evidence type: positive.

### E009-09：最终验证与 merge

What it proves: allocation、cache 和 review fixes 在 merge 前通过。

Artifact: PR #10；merge `548ecd4`；Issue #9 closeout comment。

Key numbers: fully initialized worktree 51 tests passed；7 minimal bundle smoke；最终 reviewer 无 actionable correctness issue。

Evidence type: validation.

### E009-10：8 MB 均匀分配的 Linux 配对结果

What it proves: 在本次四个 R=1 场景上，均匀分配相对hash不变或更快，纯带宽理论差距全部低于8%。

Artifact: 与 E006-11 相同的正式批次；`ara/evidence/archive/issue6_linux_clos_reproduction/RESULTS.md` 明确区分历史hash、本次hash和本次round_robin。

Key numbers: round_robin时间166.208/85.119/249.999/127.660us，gap为3.88/6.39875/4.16625/6.38333%，平均5.20708%；相对本次hash时延下降0/1.9660/2.0050/2.5719%。每逻辑流小包数差<=1，PFC事件全0；仅R=1四拓扑，不推广到全网格或1MiB。

Evidence type: positive bounded allocation comparison with explicit coverage limits.

### E009-11：11个扩规模单层Clos配置的固定版本重复验证

What it proves: 已选择的8/16/32卡R=1均匀分配配置可以在同一Linux构建上稳定复跑，但不能推广全部场景低于8%。

Artifact: `ara/evidence/archive/issue6_linux_clos_scaling/RESULTS.md`；工作区外层 `outputs/clos_scaling_20260916/clos_scaling_20260916_core_8QrZpA` 与 `clos_scaling_20260916_extended_ftlIDF`，两者均保留scaling_audit.json/.md、完整输入、FCT及校准trace。工具为同父目录analyze_scaling.py和run_scaling.sh。

Key numbers: 11配置、22性能运行，两遍逐纳秒一致；两个audit均PASS/0 errors/0 missing。共41184条FCT和41184个校准QP逐跳核验；差距2.9975%～8.367142857%，10配置低于8%。8/2/4为151.714us，高于140us理想值8.36714%，保留未调参。time-v累计命令时间305.76秒，最大MaxRSS253748KiB，不是整机总峰值。实际ELF指纹与昨日相同。

Evidence type: bounded positive scaling evidence with explicit non-target row and strengthened actual-input checks.

### E009-12：32卡双链路PFC事件与解释边界

What it proves: 本批32/2/2达到过流控阈值，不能称为无拥塞；事件数不等于丢包数或可直接相加的完成时间损失。

Artifact: core_8QrZpA的first/repeat下32/2/2正式案例output/pfc.txt；二者SHA256均为 `38604fc1770b2d4336ebb3932319316f68bd74f586bec6899987bc5fd0b7a2b2`。固定ASTRA源码qbb-net-device.cc和服务器实际common.h:140-144用于解释接收事件字段。

Key numbers: 每遍312条=156条收到pause+156条收到resume，1241.436～1260.041us，任务完成1293.096us、gap4.28194%。事件来自31卡、39个接口，各接口最后恢复。本批其他10配置PFC均0，包括gap8.36714%的8/2/4。

Evidence type: raw event analysis; causal latency contribution remains unresolved, formal full-packet trace disabled.

### E009-13：用户要求先做扎实当前阶段

What it proves: 优先级改为检查较大差距、能否优化及失败能否恢复，暂停求解器和新拓扑推进。

Artifact: `ara/evidence/archive/issue9_clos_gap_diagnosis/ExecPlan.md` 的User Raw Prompts保留2026-09-16用户原文。

Evidence type: user requirement.

### E009-14：全量逐包轨迹与实际源码定位ACK集中

What it proves: 当前普通路由仅保留每邻居最后平行接口，使ACK集中；原两个目标的时间差与该瓶颈的链路工作量差高度吻合。

Artifact: `ara/evidence/archive/issue9_clos_gap_diagnosis/RESULTS.md`；外层outputs/clos_diagnosis_20260916下clos_diagnosis_20260916_Y5QyUr、full_n8_m2_q4_trace_audit.json、full_n8_m4_q2_trace_audit.json、trace_findings.md、gap_static.py/.json/.md、common_header_actual.h。头文件SHA256为2a08f0a225102c945f266bef4bcf07c2956f4ace9bb88a0c81ac0c0127211f73；归档SHA256 a38770a142ca6fec33ece673a7368d326fb9f02f03867668d160bcb60c627e2a。

Key numbers: 8次原配置诊断，10752条FCT独立验收PASS；8MB trace开关精确复现151714/148855ns。每份全量轨迹1203664记录、448000000字节、109424唯一包。Q4/Q2的ACK占用32/128与64/128有向端口，最忙链路发送占用149643/146773ns。实际源码nbr2if覆盖平行接口，与轨迹一致。4MB时间78171/75464ns，16MB301371/295625ns（各一次诊断）。

Evidence type: source inspection, trace conservation, per-link modeled timing and bounded sensitivity experiment; no hardware timing claim.

### E009-15：只补ACK回程缺失接口的受控候选

What it proves: 在4个指定配置中，只改变普通回程路由候选可复现改善；正向负载、ET、字节、协议和理论分母未变，Q1真no-op。

Artifact: 同父目录clos_ack_candidate_20260916_HWL1Gq、candidate_audit.json、candidate_n8_m2_q4_trace_audit.json、candidate_n8_m4_q2_trace_audit.json、ack_routes.py及run_ack_candidate.py/.sh。归档SHA256为5a2b0d08a0328c6573a11385edf16687d1ebb9a77d6b7e8adee03882e4270b8d。

Key numbers: 4配置8次，两遍相同；8/2/4、8/4/2、8/2/1、32/2/2分别147292/147006/579554/1280798ns，gap5.20857/5.00429/3.49179/3.29016%。新增路由384/256/0/2048；21472条FCT与224个ET文件核验PASS。两目标完整trace数据逐端口负载不变、ACK总数不变、覆盖均128/128端口；32卡PFC从312条变0，但未隔离PFC单独耗时。尚未集成默认实现。

Evidence type: controlled input-only candidate with repeated performance, negative control, larger-case regression and independent input/trace audits.

### E014-07：用户要求 scale-up 真实性优先及有条件合并

What it proves: 研究以 scale-up/NVLink 为参考，并参考 RDMA；理论差距超过8%可以接受但须有合理证据，不为好看数据造网络。两位自动 reviewer 都同意后才允许 merge。

Artifact: `docs/plans/issue14_clos_return_routes/ExecPlan.md` 本次新增 User Raw Prompts，逐字保存两条用户要求。

Evidence type: user requirement and merge authorization condition, not hardware validation.

### E014-08：自动 review 的增量来源缺口及真实修复验收

What it proves: legacy-only 增量入口现在核验所保留 complete 成功行的当前实际构建及配置，generate-only 无法 live 核验时拒绝保留；混合报告摘要分策略。生成输入/数据面未变。

Artifact: [Codex review](https://github.com/tonyhaohan/mcnf-sim-bridge/pull/15#issuecomment-5695706739)、[Claude review](https://github.com/tonyhaohan/mcnf-sim-bridge/pull/15#issuecomment-5695797632)；两份脚本/测试 diff；远端 `/home/mcnfsim/mcnf-runs/issue14-review-20260916-e7SuKd`；外层 `outputs/clos_return_routes_review_20260916/` 的运行/启动脚本、review_audit.json、Linux日志与来源清单。源 overlay SHA256 `f0e788a01fa0c2166861d889ca0963c72519115e94a389df9316c3e6394221e1`，审计 JSON SHA256 `0ec9bd66e360763509863e088e54cf138d98de2c10999d2f2227592c3a8486d6`。

Key numbers: 新反例先得到11 failed/7 passed，修复后 focused65 passed；Linux187 passed/1 skipped。新 mixed root 先 complete 再 legacy，8/2/4重现147292/151714ns，每次1792 FCT、448000000B。两策略实际拓扑/QP配置/children/FCT均与原实验 SHA相同；8个原始文件未变。不同库身份、旧配置指纹、generate-only三项反例拒绝，原 mixed summary/report未改写。历史8MB/4MB数表不因本补丁改动。

Evidence type: counterexample-driven code repair and independently checked real integration run; not a full new matrix or hardware calibration.

Second review: [Claude comment](https://github.com/tonyhaohan/mcnf-sim-bridge/pull/15#issuecomment-5696221933) exposed same-label generate-only overwrite. Counterexample1 failed/2 passed before fix, then benchmark68 passed; added independent ACK coverage CLI and20 synthetic parser tests. Linux210 passed/1 skipped. Remote `issue14-review-20260916-e7SuKd/review-round2` validates three CLI rejections on a real-result copy (165 files unchanged) and all four original complete traces (each1203664 records/218848 ACK dequeues); every port count and trace SHA match prior independent audit. New audit SHA256 `0909e7f69597c00c681ce06dd146227969da0d5f565cf0931cfad851fde495ee`, four-file source overlay `c83d2c005ccde144e673aba2e7f8691c4104153d18dd36d68bf0ab98a5c5cd60`. Source entry `scripts/audit_clos_return_coverage.py`, scoped pullback `outputs/clos_return_routes_review_20260916/round2/`. Frozen-case expected coverage is not a universal hash-uniformity claim; no new performance simulation.

### E014-09：静态共享链路尾部负载的六例核算

What it proves: 实际4096B分配在4MB8/2/4产生静态不均，但此项容量下限增量不足以解释全部8.58286%理论差距。

Artifact: `docs/plans/issue14_clos_return_routes/SCALEUP_MODEL_BOUNDARY.md`；外层 `outputs/scaleup_model_audit_20260916/audit_payload_tail.py`、`payload_tail_audit.json`、`payload_tail_findings.md`。结果及重复文件SHA256 `b8ced171eac6fbc1bba94d2ba3e1ca7f168955f1aa7161187f9a5cb0e97d631b`，脚本SHA256 `0fd23a18ce161f2a0c4e14fa2105e224a3e9a797982de39704ef448c10ec00e2`。

Key numbers: 4MB8/2/4最大有向链路3555328B，理想3500000B；容量下限71.10656us vs70us，增量1.5808%；实际76.008us仍高出4.90144us。两个8MB案例容量下限同140.56448us。六配置重建的规范/原始SHA均等于正式audit，逐child FCT匹配，独立闭式计算一致；两例8MB还匹配已有逐链路full-trace分析。

Evidence type: frozen-source offline reconstruction bound to original configuration and FCT evidence;4/16MB not full-trace measurement; no new simulations or NVLink claims.

### E014-10：NVLink/RDMA 原始资料与模型边界

What it proves: 具体 NVSwitch 产品拓扑、单向/双向带宽、代际可靠性与 RDMA 多QP机制须分别依据原始资料；现有统一Q、400Gbps、4096B/QP模型不能直接称为已校准NVLink。

Artifact: `docs/plans/issue14_clos_return_routes/SCALEUP_MODEL_BOUNDARY.md` 的六条 NVIDIA 官方来源及逐项限制；核验日期2026-09-16。H100每GPU到四交换机4/4/5/5链路，NVLink4每方向每链路25GB/s，18链路双向合计900GB/s。NVLink6公开credit说明不倒推H100参数，NCCL的IB多QP文档不作为NVLink分流规范。

Evidence type: primary documentation and explicit modeling limitations; no target-hardware calibration or implemented NVLink backend.

后续入口预查：同ASTRA源码提交下 `examples/network/analytical/HGX-H100-validated.yml` 与对应 congestion-aware 运行脚本提供8 NPU Switch抽象（400GB/s、936.25ns）。未初始化/运行该解析子模块，未证明多重边、显式求解路径或硬件校准；不从文件名推导本项目已经验证，细节见模型边界文档。

## Issue #16：双层 CLOS 四卡小例子

### E016-01：用户确认先做小规模双层验证

What it proves: 用户要求真实性优先，按Issue、分支和ARA维护，并在2026-09-17授权开始小例子、路径/时间核验及NodeArcResult只读预查；不是授权同时大改solver或NVLink模型。

Artifact: `docs/plans/issue16_double_clos_smoke/ExecPlan.md` 的User Raw Prompts与设计契约；[Issue16](https://github.com/tonyhaohan/mcnf-sim-bridge/issues/16)，已核验Development关联分支`codex/16-double-clos-smoke`。

Evidence type: user requirement and bounded implementation decision; local review does not replace the two online reviews required before merge.

### E016-02：双层入口、独立逐跳审计与反例测试

What it proves: 新入口构造四种限定案例，按实际有向物理链路计算载荷下限，拒绝覆盖目录，保存失败，区分generated与真实运行；审计不调用输入生成器证明自身正确。

Artifact: `scripts/run_double_clos_smoke.py`、`scripts/audit_double_clos.py`和对应两个测试文件。运行快照为主分支3ee184c加四个新文件，外层`outputs/double_clos_20260917/source-v1.tar.gz`，SHA256 `75c8898c988e3d20ef7bcf4f15fe8fa3bd21a6295bcdd4c4c89998e484dbc422`。

Key numbers: v1新增51测试通过，Linux全套261 passed/1 skipped；后续仅审计增加配置文件/包长/trace一致性及低于容量下限的11项负例/边界测试，新测试合计62 passed。最终Linux全套272 passed/1 skipped，ARA和原12次离线复验通过；Windows271 passed/1 skipped/1个已有Darwin路径分隔测试失败。原7例minimal另外真实回归成功，不计入双层12次。

Evidence type: code inspection, synthetic positive/negative tests and real Linux test log; tests alone are not simulator or hardware evidence.

### E016-03：12次真实运行与原始证据独立重审

What it proves: 当前四卡、相邻节点单物理链接、400Gbps每方向/500ns、4096B/R1/native ACK 的四种合成案例使用预期路径、完成数据传输并逐纳秒重复；共享接入/上层负载没有被绕过。

Artifact: `docs/plans/issue16_double_clos_smoke/RESULTS.md`、`report_summary.json`；远端`/home/mcnfsim/mcnf-runs/issue16-double-clos-20260917-9w0erc`；外层`outputs/double_clos_20260917/evidence-v1`保留原始ET/输入/trace/FCT/日志。证据压缩包SHA256 `178ea604abb515316b6a08a8ba1398b392b2715685bc6bbee45d690808358c60`。`verify_pullback.py`和`pullback_audit.json`为加固后的离线复验，非新仿真。ASTRA181c785，ELF SHA256 `7f9db19d50dafbe8d371c9f64cbef8b9e7b27cb7794fb1c62e6be8956ade67f4`。

Key numbers: 4校准+8性能，12全部成功；105FCT、416143360B。8份全trace958157记录、70个QP运行实例、208143360B。四性能时间164195/166363/660489/496749ns，重复精确相同；下限160/160/640/480us，差距2.621875/3.976875/3.20140625/3.489375%。每组first/repeat20个输入仅trace开关不同，FCT哈希相同。全批运行命令7.75秒、MaxRSS248480KiB，不含部署/pytest、不是整机总峰值。

Evidence type: frozen-source real ASTRA run, full-trace conservation/path audit, exact repeats and independent raw-file verification. Does not prove full two-tier coverage, solver Allreduce, isolated residual causality or NVLink hardware accuracy.

### E016-04：已有解持久化与多阶段接口缺口的只读预查

What it proves: solver已有save/load artifact，不必每次重求；裸NodeArcResult及当前QP转换不足以完整保留多阶段Allreduce语义。

Artifact: `docs/plans/issue16_double_clos_smoke/NODEARC_INTERFACE_PRECHECK.md`；MCNF_tree版本7cba8c9与0a03dd8的`artifacts.py`、`linear_model.py`、artifact tests，以及bridge `astra_ns3_schedule.py`、`generate_qp_bindings.py`。

Evidence type: pinned-version read-only code inventory. No solver run, no artifact round-trip executed this session, no solver source modification.

## Issue #17：双层CLOS扩规模与高差距

### E017-01：固定扩规模矩阵与真实性约束

What it proves: 用户在四卡结果之后要求“挺好，接着按照计划推进”，据此先扩卡数和数据量，继续Issue/分支/ARA记录，不为低gap改网络，不提前接solver。

Artifact: `docs/plans/issue17_double_clos_scaling/ExecPlan.md`；[Issue17](https://github.com/tonyhaohan/mcnf-sim-bridge/issues/17)，Development关联`codex/17-double-clos-scaling`，基于尚未合并的Issue16提交c9579bf。

Evidence type: user requirement and predeclared bounded matrix, not an observed result.

### E017-02：有限参数化、检查内存修复及旧证据回归

What it proves: 仅扩bridge实验入口与检查工具，完成包跳状态释放不弱化原验证；默认四卡输入保持。

Artifact: `scripts/run_double_clos_smoke.py`、`scripts/audit_double_clos.py`和对应测试。外层`outputs/double_clos_scaling_20260917/source-v1.provenance.json`记录c9579bf加四个未提交overlay；源码包SHA256 `9fd09e5ca10859266dc377c23f1bb396f364b52590e00f8204d5baf2724acf61`。

Key numbers: focused114 passed；Linux324 passed/1 skipped；Windows323 passed/1 skipped/1个旧Darwin路径分隔失败。旧12份证据除新增active-key峰值外逐对象相同，144个默认Windows输入原始hash相同。正式批前修复包装延迟字符串500ns/0.0005000ms等价但误拒绝问题，没有由此产生失败的真实批次。

Evidence type: implementation tests, frozen-source hashes and offline old-evidence regression; memory key peaks are not whole-process bytes.

### E017-03：24次新增实跑及独立原始文件核验

What it proves: 指定8/16卡、1/2/4上层和4/8/16MB矩阵真实完成且可重复，但16卡4上层稳定高于纯带宽下限33%～35%，不能宣称性能全面验收。

Artifact: `docs/plans/issue17_double_clos_scaling/RESULTS.md`及`report_summary.json`；远端`/home/mcnfsim/mcnf-runs/issue17-double-clos-scaling-20260917-SbNiSI`。本地外层`outputs/double_clos_scaling_20260917/evidence-v1`、固定包装、独立审核、取回核验脚本。小证据包SHA256 `e7267aa1b9678b15b71291c187cc38ea4b1d9c3bbcf72fc579ea84aa135d6643`；独立审核JSON SHA256 `129f33f7361f237bc7fff0ce9eb6debcb9e3f909acab5872be64e2b497a3f826`。完整大trace留服务器，取回1812文件hash一致。

Key numbers: 新增24次8328FCT、23819370496B，16份完整trace51058484记录。8点性能2628.959/1323.713/1152.163/10502.346/5259.168/3447.875/1704.981/6934.400us；均精确重复。原4卡另回归12次、另7例minimal真实通过；36次主批1152个输入hash独立重算。主批361.41秒、maxRSS343572KiB，不是整机峰值。ASTRA181c785与原ELF/18库身份保持。

Evidence type: real frozen-source executions plus independent raw-input/FCT/capacity review. Second reviewer hashes/counts large traces, not a second complete per-hop decoder. Pure-capacity gap is not hardware error; full Allreduce and causal attribution remain outside this evidence.

### E017-04：高差距的同组尾部、共享暂停与逐链路空闲

What it proves: 16卡四上层的任务尾部是同组传输；存在大量GPU接入口内部空闲和同priority暂停，静态分片不均不足以解释高gap。

Artifact: 外层`outputs/double_clos_scaling_20260917/inspect_pfc_fct.py`、`pfc_review.json`、`n16_s4_d8000000_serialization.json`及其版本绑定的离线分析脚本；原始FCT/PFC/full trace与实际181c785的`common.h`、`qbb-net-device.cc`、`qbb-helper.cc`。精确文件指纹见本轮`report_summary.json`。

Key numbers: S4在4/8/16MB时同组最后1704.981/3447.875/6934.400us，跨组1339.752/2652.395/5278.526us；S2/8MB同组1962.865us早于跨组5259.168us。四份PFC trace按source-QP计数没有额外数据重发、没有drop/NACK；收到的PFC全部GPU接口priority3，暂停恢复成对。ACK_HIGH_PRIO0令ACK与数据同为priority3。S4/8MB每GPU发送接口忙2460.960us、内部idle984.327～985.914us，上层链路末次发送结束后还空闲约802～805us才整任务完成。调度轮询eligible QP，不是按逻辑流平均。

Evidence type: offline raw trace/FCT/PFC decoding and source corroboration, no new performance run or simulator change. Does not isolate each mechanism's causal delay or establish a more realistic alternative scheduler; simulator serialization is not hardware wire accounting.

### E017-05：暂停与真实发送区间的精确交集及固定版本流控源码

What it proves: 四上层8MB的GPU口95.32%～95.94%空闲与priority3暂停重合，最后跨组源发送结束时每GPU仍有约42MB组内数据未发；该现象在4/16MB也存在，S1/S2对照无此组内剩余。当前CC12并未启用反馈调速，不能按配置名猜测动态降速或变窗。

Artifact: `docs/plans/issue17_double_clos_scaling/DIAGNOSIS.md`；外层`outputs/double_clos_pause_diagnosis_20260917/`中`analyze_gpu_pause.py`、27项合成测试、五份`*_pause.json`、`pause_diagnosis_summary.json`、命令/资源清单和`source_review*`。原始trace仍在SbNiSI批，本次派生结果另存远端`issue17-pause-diagnosis-20260917-YQE9Oo`。分析器SHA256 `5f4f48d7918a9fa343c017284414f8dd805a5431dfa7c65d35e76b60f947a81c`；九份源码的证据JSON SHA256 `c006fa5a113b72134c00306ab2812c1913c2bb0897452fc34539f8df187cb94c`。

Key numbers: GPU0为2460.960us忙、943.354us暂停空闲、43.561us其余空闲；和为3447.875us。暂停总958.458us含15.104us已起发包的继续发送。全16卡四项恒等式和原有忙闲总量一致，五trace均无暂停后违规新起发。全局跨组源发完2545.475us时同组剩41.725440～41.979392MB/GPU。五份只读分析38.66s/maxRSS84340KiB，不是新增仿真运行；报告取回SHA重验。

Evidence type: Exact per-port temporal accounting plus pinned-source semantics, not PFC-off causal ablation, fixed-QP-share proof or physical hardware calibration. Pause/idle lengths cannot be added across GPUs or directly added to the ideal capacity lower bound. Fixed configured windows108100/216200B are not measured RTT; S2 window-blocking remains to be reconstructed.

### E017-06：累计ACK窗口重建解释不同上层数下的QP资格差异

What it proves: 在固定CC12/400Gbps/BDP窗口的三份旧8MB trace中，S4的512条跨组QP逐条窗口受限时间为0；S2/S1跨组QP待发时间的91.3126%/97.3164%为窗口受限。不能再把所有配置的QP始终同等可发送当成事实。

Artifact: 同一`DIAGNOSIS.md`第5节；外层`outputs/double_clos_pause_diagnosis_20260917/`中`analyze_gpu_windows.py`、`test_analyze_gpu_windows.py`、三份`*_windows.json`、`window_manifest.json`及资源记录。原始trace不变；分析器SHA256 `58794e700a693ba8666d778711d851339162e409cb7ad9121da83a9ed3adb94f`。报告逐QP保存sent/acked/window/最大在途字节及窗口受限时长，包含来源构建和原始trace SHA。

Key numbers: 26项合成测试通过；三份旧trace离线分析39.44秒/maxRSS50712KiB。S4 GPU0其余空闲43.561us精确分为所有待发QP窗口满36.263us和本卡无待发数据7.298us；S2为2430.281+116.414=2546.695us。全48个GPU口无窗口可发数据或排队ACK却正时长空闲的未解释区间；无非法超窗起发、暂停起发、重传或发送重叠；逐QP积分与聚合积分一致。独立100种子状态oracle及48GPU/1232QP报告对照通过，`independent_review_windows.json` SHA256为`6e28ff5d8b022b207a4e0232218d26e2a4375976b12292252319520e2b2f2d39`；该独立核对没有声称重新读取本地缺失的大trace。

Evidence type: Source-constrained cumulative-ACK state reconstruction, not another simulator run, full RR/callback reimplementation or a causal intervention. QP-time ratios count concurrent QPs and are not collective time penalties. Hardware flow-control/fairness appropriateness remains open.

### E017-07：一手网络资料与固定模型契约核查

What it proves: 共享优先级暂停和多QP资源竞争有真实网络依据，但不能据此认定冻结模型逐包轮询、固定窗口、暂停时序等于任一商用NIC或NVLink。现有证据不足以仅凭降低gap选择默认修改。

Artifact: `docs/plans/issue17_double_clos_scaling/MODEL_REVIEW.md`；外层`outputs/double_clos_model_review_20260917/`的`pfc_sources.md`、`rdma_sources.md/.json`、`nvlink_sources.md`和`local_options.md`。包含Cisco/NVIDIA/rdma-core官方资料、Justitia/DCQCN/CAIS原论文的URL、读取日期、释义和范围；本地接口行号与实际181c785源码取证核对。旧源码证据SHA仍为`c006fa5a113b72134c00306ab2812c1913c2bb0897452fc34539f8df187cb94c`。

Key findings: 正常链路PFC接收分支将正暂停值转为Boolean锁定，没有按该值安排到期；这与完整定时线协议不同，但未证明是高gap的因果。未执行的同组4QP候选使每GPU同组/跨组QP从7/32变为28/32，同组每逻辑流窗口预算108100→432400B，跨组仍864800B；不是单独公平性消融。NVLink6信用机制不能直接填充H100参数，P100链路级ACK不等价RDMA端到端ACK。CNP高优先依据也不等于普通ACK依据。

Evidence type: Primary-source literature review and pinned-code/interface comparison, not new performance runs, counterfactual speedup measurements or hardware validation. Proposed runner and simulator changes were not implemented; original results and default behavior are unchanged.

## Issue #18

### E018-01：用户批准单点QP布局对照，冻结物理网络和旧默认

What it proves: 用户“可以”批准同组每卡对1QP对4QP、跨组不变的有限实验，不批准修改仿真器、默认配置或PR/merge。

Artifact: Issue18、关联分支`codex/18-double-clos-qp-control`，`docs/plans/issue18_double_clos_qp_control/ExecPlan.md`及其User Raw Prompts。基线ea8d278，保留Issue17未提交研究记录。

Evidence type: requirement and declared experimental contract; not a performance finding.

### E018-02：六次真实配对、输入不变量及取回核验

What it proves: 相同物理网络/业务字节/跨组输入下，原3447.875us可精确复现，候选为2634.101us，两者首遍/重复FCT和完成时间逐字节一致。固定2560us下限对应34.682617%与2.894570%，不是硬件误差。

Artifact: `docs/plans/issue18_double_clos_qp_control/RESULTS.md`、`report_summary.json`。外层`outputs/double_clos_qp_control_20260917/`内源码snapshot、provenance、run_control.py、audit_pair.py、pullback_audit.json及`evidence-v1/`；远端`issue18-qp-control-20260917-3pygAq`保留大trace。source-v1.tar.gz SHA256 `de5e75d5c1e41b44c7fea7d803fd7dc24943369624de23170c604d7df1dd999b`；不是干净Git提交。结果归档SHA256 `4a6a735392c847cd9a907e9cf1bce2f6b7f7b9ad2af1fb98c0284c29a1c38c41`；独立审核JSON SHA256 `3226438bd9ba1a56af7b169189459d79fb8a64cc185e872063a6d4cf8379c97c`。

Key numbers: 全网624→960QP，112→448同组QP，512跨组QP、624完整路径、240有向逻辑流、1.92GB业务字节保持。Linux349 passed/1 skipped，Windows348 passed/1 skipped/1个既有路径分隔失败；100项runner测试通过。六次实跑4752条FCT，114.82秒/maxRSS267460KiB；另有1次真实minimal，7例minimal仅生成。拉回373文件、264输入哈希校验通过，7个mix.tr文件含无trace头文件留远端，不声称本地重读大trace。

Evidence type: Source-bound real paired execution, full-trace audit and independent raw-input/FCT/repeat verification. Per-QP4096B校准总量随QP数变化；聚合窗口预算也变化，非纯公平性消融。独立脚本对CSV/ET仅做哈希，不声称独立解释其语义。

### E018-03：新配对的暂停、源端尾部与窗口状态

What it proves: 候选在相同业务字节下减少了暂停重合空闲；GPU0忙时不变2460.960us，暂停重合空闲943.354→85.712us，其余空闲43.561→87.429us。两者跨组QP均无窗口受限待发时长；原同组QP待发时间中2.101326%受窗口限制，候选为0。

Artifact: 同上RESULTS.md，外层`evidence-v1/analysis/{comparison,manifest,baseline_pause,baseline_windows,candidate_pause,candidate_windows}.json`，`analyze_pair.py`及15项合成测试；旧两个分析器未修改，SHA见manifest。wrapper SHA256 `790f43f048e8807dcc31f5e63a9bb54265ff3ef8408a7e0ff5889767b660229b`。分析用时41.13秒/maxRSS55264KiB。

Evidence type: Frozen-source-constrained interval and cumulative-ACK reconstruction, not full scheduler replay. Per-GPU时长并行，不能相加为任务损失；交集不等于关闭PFC的收益。QP数量、聚合窗口与排队过程同时变化，真实NIC/NVLink标定仍未完成。

## Issue #19

### E019-01：冻结四点QP布局回归而不推广默认

What it proves: 用户确认不同网络允许不同QP绑定规则后要求开始工作，本轮限制为N8/S4/8MB和N16/S4/4、8、16MB，两配置各三次；不修改物理网络、每QP窗口、PFC、模拟器或默认。

Artifact: GitHub Issue #19；`docs/plans/issue19_double_clos_qp_matrix/ExecPlan.md`的原话、范围、源码与工具哈希；分支`codex/19-double-clos-qp-matrix`。运行来源复用Issue18的非干净提交归档`de5e75d5c1e41b44c7fea7d803fd7dc24943369624de23170c604d7df1dd999b`。

Evidence type: User-scoped finite experiment and provenance freeze, not approval of a universal hardware model or default promotion.

### E019-02：24次真实运行保留16卡收益和8卡回退

What it proves: 四点输入、业务字节、逐路径负载、FCT与重复核查通过；16卡三个数据量改善22.63931%～24.15125%，8卡8MB反而慢1.171us。旧baseline的输入/time/FCT及8MB候选anchor精确复现，不能推广为二进制trace逐字节相同。

Artifact: `docs/plans/issue19_double_clos_qp_matrix/RESULTS.md`、`report_summary.json`；外层`outputs/double_clos_qp_matrix_20260917/{run_matrix.py,audit_pair.py,verify_pullback.py,pullback_audit.json,evidence-v1/}`。完整trace留在远端`issue19-qp-matrix-20260917-GH0pSd`。小证据归档SHA256 `1aa0ebf429643314a104ec949349d54322283714ff9c6158364e3d538c2785f9`；四审计JSON哈希收录机器报告。Linux冻结源349 passed/1 skipped；新包装测试77项通过。

Key numbers: 24run、15384FCT、28693004288B；校准21004288B、性能28672000000B。取回1300文件和960输入哈希核验通过。主批426.35s/maxRSS344928KiB。N8总QP152→224，N16为624→960，性能载荷和容量下限逐点不变。候选gap为2.97625%、3.04570%、2.89457%、2.72766%，均是连续业务容量下限差而非硬件误差。

Evidence type: Real finite paired runs with independent raw-input/FCT/path-payload audit and bytewise pullback verification; no independent full CSV/ET semantic decoder. Trace-off repeats are not full-trace validations or independent statistical samples.

### E019-03：逐口区间解释收益与非单调性，保留因果限制

What it proves: 8卡两配置都无PFC或窗口受限待发，忙时相同，1.171us差异体现在未暂停空闲/收尾。16卡三点忙时不变、暂停重合空闲降低，同组未发尾部由约21/42/84MB缩到最多6912/13824/0B；数据没有消失。N16D8的已解析暂停/窗口指标与Issue18相同，原始trace SHA不同，不推断差异原因。

Artifact: 外层`evidence-v1/analysis/<point>/{comparison,manifest,baseline_pause,baseline_windows,candidate_pause,candidate_windows}.json`及资源记录；`analyze_pair.py`和27项包装测试；旧分析器原SHA及53项测试保持。逐点精确统计、文件哈希与解释见RESULTS.md和report_summary.json。

Evidence type: Source-constrained eight-trace interval and cumulative-ACK reconstruction, not full native scheduler replay. QP数量和聚合窗口共同变化；暂停/空闲交集不能等同反事实收益，各GPU时长不能相加。具体NIC/NVLink真实性问题保持开放。

Supplement: 针对N16D8两策略的Issue18/19不同trace SHA，以原审计哈希绑定进行只读逐记录比较。基线8220750条、候选8179044条的头部及全部活动声明字段均一致（包括qlen/ECN/ts/flags）；仅填充/非活动存储不同，不推断该存储取值原因。外层`compare_frozen_traces.py`及18项测试、`trace_fields_baseline.json`/`trace_fields_candidate.json`保存新增证据，JSON SHA分别`96a7022f65ab9060d145e5db23c0ff485de6482b46e3f0a21aa8672241cbe895`/`67a336cc704d4bec0991da0d81ce7330103ddd6ae046bf3a7844df0c53045df5`。原1300文件证据包不改写，不计为新仿真；不声称所有未记录内部状态一致。

## Issue #20

### E020-01：用户澄清后只扩32卡四上层，不把4QP推广到所有场景

What it proves: 用户接受8卡轻微回退，确认不是全场景改4QP，要求继续把双层CLOS做扎实、实事求是。当前范围为N16/8MB旧对照、N32/1MB先导及核验/资源通过后的4MB；保留原默认和两配置，无低gap门槛。

Artifact: GitHub Issue #20（只含本轮计划，不含未获外发确认的旧结果）、关联分支`codex/20-double-clos-n32`；`docs/plans/issue20_double_clos_n32/ExecPlan.md`原话、模型边界与阶段门槛。新源码归档SHA2337205f289c3340057285f71ec3440cbfd1d7b4272d8e6c9fe1f2428afef317仅替换旧归档的runner与对应测试，六个其他运行文件及仿真器不变。

Evidence type: User-scoped experiment decision with bounded implementation/tests, not advance evidence of successful N32 simulations or hardware calibration. Windows378 passed/1 skipped/既有路径分隔失败；冻结源Linux379 passed/1 skipped；新增外层审计/分析/阶段门控123项通过。真正运行结果另记，input-only和mock不算仿真。

### E020-02：32卡有限真实矩阵、旧对照和取回完整性

What it proves: 三点18次真实运行、六套性能重复与三对独立输入/FCT/链路载荷核验通过；N16/8MB旧对照输入/time/FCT保持。N32/1MB原1464.489us、候选1318.466us；4MB原6093.800us、候选5264.348us。QP数量2528→3968，性能数据和每条有向物理链路负载不变。

Artifact: `docs/plans/issue20_double_clos_n32/{ExecPlan.md,RESULTS.md,report_summary.json}`；外层`outputs/double_clos_n32_20260917/{run_matrix.py,audit_pair.py,verify_pullback.py,pullback_audit.json,evidence-v1/}`；远端`issue20-double-clos-n32-20260917-gjya1Y`保留大trace。小证据包SHA256 `42bcaee6627fdb2c4d26ba4876c83581dc0f581a016d85bf40fe03c916f010e9`。运行源精确overlay与二进制哈希见机器报告。

Key numbers: 18run、43728FCT、27579703296B，其中校准59703296B、性能27520000000B；1528原始小文件、1176输入哈希验证。主批596.31秒/maxRSS377848KiB、0 swaps；结果约3.3GiB。额外7个minimal仅生成，1次真实minimal单独计数。Linux379 passed/1 skipped，Windows既有路径分隔失败保留。取回后独立逐FCT/重复/旧anchor及三次fresh audit复核PASS，外层`independent-review.json`SHAee668d24cedee3c6fbe02c7ae315f498147ded0df285fb372b1a9138141ebbe7。

Evidence type: Real finite paired runs, source-bound full-trace auditing and independent raw-input/FCT/load checks with cryptographic pullback binding. Calibration bytes differ with QP count. No independent complete CSV/ET semantic decoder, statistical confidence claim or local full-trace re-decoding; no universal default or hardware-accuracy claim.

### E020-03：32卡暂停次数增加却更快，分开报告时长与次数

What it proves: 两32卡点原配置最终同组收尾，候选跨组收尾。同组未发尾部由每卡约10.69～11.19MB和44.51～44.95MB缩到0和最多2304B。忙时不变635.779/2542.992us，平均暂停重合空闲799.230→568.733us、3520.894→2598.140us；但pause事件7166→12965、32298→62342。不是通过减少暂停次数提速。

Artifact: 外层`evidence-v1/analysis/<point>/{comparison,manifest,baseline_pause,baseline_windows,candidate_pause,candidate_windows}.json`与原FCT；三个comparison哈希见`report_summary.json`。wrapper `analyze_pair.py`SHA563af8e1d0b14c2565fd56321d59d878bfd4519d96978becd9a25cc801b34e98；底层两个分析器哈希保持。

Evidence type: Six real full-trace, frozen-source-constrained interval/cumulative-ACK reconstructions; source completion distinct from FCT. QP数量与聚合窗口同时变化，不能把缩短全部归因调度公平，暂停交集不代表关闭PFC的反事实收益。具体NIC/NVLink真实性及I017-N05保持开放。

## Issue #11

### E011-01：ARA 原论文与官方 artifact

What it proves: 原论文将 `trace/exploration_tree.yaml` 定义为一个 ARA artifact 的 complete research DAG；作者自己的 artifact 用一张图积累多个 session。

Artifact: <https://ar5iv.labs.arxiv.org/html/2604.24658>；<https://github.com/ARA-Labs/Agent-Native-Research-Artifact/tree/main/docs/the-ara-of-ara>。

Evidence type: protocol source.

### E011-02：项目全局 DAG 要求

What it proves: 用户确认从科学研究角度采用全局 DAG，并要求所有项目参与者服从 ARA 维护规范。

Artifact: GitHub Issue #11；`docs/plans/issue11_restore_ara_research_management/ExecPlan.md` 的 `User Raw Prompts`。

Evidence type: requirement.

### E011-03：全局 DAG 自动 enforcement

What it proves: 本地 validator 和 GitHub Actions 能拒绝第二张 DAG、cycle 和缺失 Issue view，并验证全局引用。

Artifact: `scripts/validate_ara.py`；`tests/test_ara.py`；`.github/workflows/ara-validate.yml`。

Key numbers: 当时的2026-07-12快照为32 nodes、48 edges、30 evidence、11 claims、4 sessions；structural enforcement 和 HTML freshness tests 覆盖 mandatory schema。

Evidence type: validation.
