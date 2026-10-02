---
status: active
owner: core-maintainers
last_verified: 2026-09-17
scope: mcnf-sim-bridge 项目级 ARA executable surface map
---

# Source And Executable Surfaces

## 全局 Idea 图

- Source: `ara/trace/exploration_tree.yaml`
- Generator: `scripts/render_ara_graph.py`
- Tracked output: `ara/views/global.html`
- Freshness check: `tests/test_ara_visualization.py`

## Issue #3 历史失败路线

- Historical branch: `origin/codex/3-clos-alltoall-calibration` at `7cde3ed`
- Historical ARA source: commit `2343ac1`, `ara/issue3_clos_alltoall/`
- Historical ExecPlan/report: the Issue #3 branch under `docs/plans/issue3_clos_alltoall_calibration/` and `docs/results/issue3_clos_alltoall_calibration.md`
- Successor implementation: Issue #6 bridge/ASTRA commits `06bee4e` and `181c785`

## Bridge接口层

- `scripts/generate_qp_bindings.py`：完整物理路径、QP、QP组、逻辑流映射和4KB小包 QP选择。
- `scripts/run_clos_qp_benchmark.py`：N/M/Q/R benchmark、trace calibration、allocation 对照和结果报告。
- `scripts/run_qp_reuse_smoke.py`：persistent QP reuse 验证。
- `src/mcnf_sim_bridge/interfaces/astra_ns3_schedule.py`：ASTRA bundle 输出。

## ASTRA 与 ns-3

- `repos/astra-sim/astra-sim/network_frontend/ns3/entry.h`：resolved QP configuration、path-specific alias route 和 persistent QP FIFO。
- `repos/astra-sim/extern/network_backend/ns-3/src/point-to-point/model/rdma-hw.*`：最小 persistent-QP completion 分支。
- Switch forwarding、Qbb、PFC、ECN 和拥塞控制保持原版。

## 编译缓存

- `scripts/astra_ns3_binary.py`：按 ASTRA commit SHA 缓存并校验 binary、ns-3 和 protobuf runtime libraries。
- `scripts/run_manual_astra_smoke.py`：真实 ASTRA smoke 入口和 verified runtime environment。

## Tests And Durable Reports

- `scripts/validate_ara.py`
- `tests/test_ara.py`
- `.github/workflows/ara-validate.yml`
- `tests/test_qp_bindings.py`
- `tests/test_clos_qp_benchmark.py`
- `tests/test_astra_ns3_binary.py`
- `docs/simulator/astra_ns3/QP_CONFIGURATION_REQUIREMENTS.md`
- `docs/plans/issue6_qp_config_groups/qp_per_path_coarse_results.md`
- `docs/plans/issue9_round_robin_default/allocation_comparison.md`

## Linux 单层 Clos 复现归档

- 执行计划与中文报告：`ara/evidence/archive/issue6_linux_clos_reproduction/ExecPlan.md`、`RESULTS.md`。
- 包装与验收工具：工作区外层 `outputs/clos_reproduction_20260915/run_reproduction.sh`、`analyze_reproduction.py`、`verify_native_paths.py`；后者复用仓库 `_verify_trace` 重新读取原始校准轨迹。
- 正式产物：外层 `outputs/clos_reproduction_20260915/clos_reproduction_20260915_cd9hTY/`；同名远程目录位于 `/home/mcnfsim/mcnf-smoke/experiments/`。
- 负结果：同父目录 `clos_reproduction_20260915_dXbRHT`，保留被覆盖校准的原始状态及失败验收报告。
- 运行source未修改：bridge `1d4f816`、ASTRA `181c785`；本地分支仅增加实验记录，原有历史报告不改写。

## Linux 单层 Clos 扩规模归档

2026-09-16扩规模归档：`ara/evidence/archive/issue6_linux_clos_scaling/ExecPlan.md`、`RESULTS.md`。外层 `outputs/clos_scaling_20260916` 保存包装及只读验收脚本，正式批core_8QrZpA、extended_ftlIDF及原失败批core_86J6hV。验收器复用旧审计，并增加真实qp_config、逐child FCT、独立native trace和资源指标检查；不修改仿真行为。

## 单层 Clos 差距与失败诊断

- `ara/evidence/archive/issue9_clos_gap_diagnosis/ExecPlan.md`、`RESULTS.md`。
- 外层 `outputs/clos_diagnosis_20260916` 保存隔离运行run_diagnosis.py/.sh、run_ack_candidate.py/.sh、纯输入补全ack_routes.py、独立验收audit_diagnosis.py/audit_ack_candidate.py、完整轨迹analyze_trace.py、静态核算gap_static.py及实际头文件证据。
- 正式诊断批clos_diagnosis_20260916_Y5QyUr、候选批clos_ack_candidate_20260916_HWL1Gq；原版与候选目录独立。没有修改仓库核心或默认行为。

## Issue #14 review 与 scale-up 模型边界

- `docs/plans/issue14_clos_return_routes/SCALEUP_MODEL_BOUNDARY.md`：NVIDIA 原始资料、NVLink/RDMA 边界、六个已有案例的物理链路有效字节下限；不是已实现的 NVLink 后端。
- 外层 `outputs/scaleup_model_audit_20260916/`：`audit_payload_tail.py`、`payload_tail_audit.json`、`payload_tail_findings.md`；离线核算，不新增仿真或改写原结果。
- 外层 `outputs/clos_return_routes_review_20260916/`：review 修正的源码 overlay、运行脚本、Linux 测试和 `review_audit.json`；远程原始目录 `/home/mcnfsim/mcnf-runs/issue14-review-20260916-e7SuKd`。
- 本轮 2 次真实混合策略运行单独计数，不混入原有 100 次；来源核验、报告和文档修改没有改变输入及 FCT。
- `scripts/audit_clos_return_coverage.py` 与 `tests/test_clos_return_coverage.py`：独立读取实际 ACK trace 的仓库内入口；仅显式冻结样本断言，不强制有限哈希样本满覆盖。外层同 review 目录的 `verify_round2.py`、`run_round2.sh` 记录第二轮验证。

## 双层 CLOS 小规模验证（Issue16）

- `scripts/run_double_clos_smoke.py`：固定四卡的组内/跨组P2P及单/双上层全互传；校准、全trace首遍和无trace重复独立目录。
- `scripts/audit_double_clos.py`：有向共享链路载荷、输入/FCT一致、固定Linux 56B ABI的逐包路径与数据/ACK衔接。仅单phase、legacy、每个活跃QP一个child。
- `tests/test_double_clos_smoke.py`、`tests/test_double_clos_audit.py`：构造、容量、拒绝覆盖、失败保留、配置错配、trace破损和异常完成时间反例。
- `docs/plans/issue16_double_clos_smoke/ExecPlan.md`、`RESULTS.md`、`report_summary.json`、`NODEARC_INTERFACE_PRECHECK.md`：范围、结果、可机器读取复验和未实现的solver接口契约。
- 外层`outputs/double_clos_20260917/`：源码快照、远程启动脚本、完整原始证据、独立重审脚本及结果。远程新目录为`issue16-double-clos-20260917-9w0erc`。不覆盖旧实验。
- 基础主分支3ee184c是已合并PR15的真实merge commit，与既有050db27同tree。下文旧PR状态是历史记录，不作为2026-09-17实时状态。

## 双层CLOS扩规模及高差距（Issue17）

- `scripts/run_double_clos_smoke.py`现支持限定4/8/16卡及显式4上层，保留原默认四例；`scripts/audit_double_clos.py`释放完成匹配状态，精确序列检查不变。
- `docs/plans/issue17_double_clos_scaling/ExecPlan.md`、`RESULTS.md`、`report_summary.json`记录8点24次、原四卡12次回归及高差距，不能据PASS声称贴近理想时间。
- 外层`outputs/double_clos_scaling_20260917/`保存来源冻结、运行/独立审核/取回检查和PFC/FCT、序列化离线分析。远端`issue17-double-clos-scaling-20260917-SbNiSI`保留完整大trace；本地取回原始小文件，不覆盖旧批。
- 运行来源为Issue16的c9579bf加四个显式overlay；ASTRA/ns-3与solver无改动。观察到同组尾部、共享priority3暂停、per-QP轮询和接入空闲；未实现调度优化或硬件标定。

## Issue17：只读暂停与QP资格续查

- `docs/plans/issue17_double_clos_scaling/DIAGNOSIS.md`为已有高差距的续查报告，不改写原结果或带宽下限。
- 外层`outputs/double_clos_pause_diagnosis_20260917/`保存独立分析器、测试、五个真实旧trace的派生报告、源码行段/哈希、命令和资源记录。远端新诊断目录为`issue17-pause-diagnosis-20260917-YQE9Oo`。
- 仅创建派生分析和研究记录；没有修改仿真器/运行入口/输入参数，没有新增性能运行、提交、推送、PR或merge。每张卡的暂停与空闲交集不等于关闭PFC的反事实任务收益。

## Issue17：RDMA/NVLink模型契约核查

- `docs/plans/issue17_double_clos_scaling/MODEL_REVIEW.md`区分真实机制依据、冻结源码选择与尚未建立的硬件等价；保留高差距，不将候选更快等同更真实。
- 外层`outputs/double_clos_model_review_20260917/`保存PFC、RDMA、NVLink一手来源及本地候选可实现性审阅。没有生成候选输入、远程执行或修改模拟器/bridge运行源码。
- 候选同组4QP对照需要另行授权的有限输入构造扩展和全QP校准；只是QP布局敏感性研究，不能排除聚合窗口等同时变化。

## Issue18：同组QP数量单点配对

- `scripts/run_double_clos_smoke.py`新增显式`--same-leaf-qps {1,4}`，默认1不变；旧QP地址/端口/path不变，新增同组QP共享原路径。仅runner和对应测试有执行代码修改。
- `docs/plans/issue18_double_clos_qp_control/ExecPlan.md`、`RESULTS.md`、`report_summary.json`记录N16/S4/8MB六次真实运行及解释边界，不以变快直接推广默认或声称硬件精度。
- 外层`outputs/double_clos_qp_control_20260917/`保存source-v1冻结、启动与独立审计/分析器、小证据取回及校验；完整trace保留远端`issue18-qp-control-20260917-3pygAq`。原Issue17档案不覆盖，既有物理模型问题保持open。
- 当前本地工作树路径仍名`mcnf-sim-bridge-issue17`，分支已为`codex/18-double-clos-qp-control`；此轮未commit/push/PR/merge，不把线上已关联分支当成已推送实现。

## Issue19：四点同组QP布局回归

- `docs/plans/issue19_double_clos_qp_matrix/ExecPlan.md`、`RESULTS.md`、`report_summary.json`保存有限四点、24次真实运行、原始证据映射及8卡负结果。本轮没有修改Issue18运行源码或原默认。
- 外层`outputs/double_clos_qp_matrix_20260917/`保存批处理、审计/分析包装与77项新测试、离线输入检查、小证据包和校验；远端`issue19-qp-matrix-20260917-GH0pSd`保留全部大trace。复用Issue18非干净source归档和同一ASTRA二进制，没有重新构建。
- 工作树路径仍为`mcnf-sim-bridge-issue17`，当前分支`codex/19-double-clos-qp-matrix`，保留旧未提交工作；线上分支已关联Issue不等于本地实现或本轮报告已推送。本轮无commit、push实现、PR或merge。

## Issue20：固定四上层32卡有限扩展

- `scripts/run_double_clos_smoke.py`只新增显式N32/S4允许范围及对应测试，原默认、S1/S2及旧点不变。运行源为Issue18归档的精确两文件overlay，非干净main。
- `docs/plans/issue20_double_clos_n32/{ExecPlan.md,RESULTS.md,report_summary.json}`记录三点18次真实运行、18之外的minimal、旧对照、资源、理论口径与限制。
- 外层`outputs/double_clos_n32_20260917/`保存源/工具/证据哈希、输入预检、独立审计、阶段门控和123项测试、取回证据；远端`issue20-double-clos-n32-20260917-gjya1Y`保留所有大trace。既有结果未覆盖。
- 工作树仍名`mcnf-sim-bridge-issue17`，当前分支`codex/20-double-clos-n32`，旧脏工作保留。Issue/关联分支只公开本轮计划，未发布结果、commit、push实现、PR、merge或清理。

## Key Commits and PR State（历史）


Issue #14 的正式集成入口为 `scripts/generate_qp_bindings.py`、`scripts/run_clos_qp_benchmark.py`、`scripts/astra_ns3_binary.py` 与 `scripts/run_manual_astra_smoke.py`；执行状态见 `docs/plans/issue14_clos_return_routes/ExecPlan.md`，100 次限定回归结果见同目录 `RESULTS.md`、`report_summary.json`、`html/index.html`。外层 `outputs/clos_return_routes_20260916` 保存运行、独立审计、缓存反例与报告脚本；正式远程任务为 `issue14-return-routes-20260916-46Aon8`。原 Issue 6/9 记录保留，输入候选与正式运行分开；4MB 例外不删除。旧记录 `a5409aa` 与实现/验证 `f1a847b` 已推送；PR #15 开放并关联 Issue #14，线上 ARA 检查通过，尚未合并。

- ASTRA QP implementation: `181c785`
- Bridge Issue #6 merge: `06bee4e`
- Allocation/cache implementation: `b84a64e`, `b259571`, `016d25d`
- Bridge Issue #9 merge: `548ecd4`
