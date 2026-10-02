# Issue #3 — Clos all-to-all 历史校准与显式路径契约

## 统一信息

本纪要迁移原 tonyhaohan/mcnf-sim-bridge Issue #3；源Issue： https://github.com/tonyhaohan/mcnf-sim-bridge/issues/3 。冻结来源 commit `9e2058fcca7b95389d30e81cb0e52ffe03e2e930`。以下时间与结果属于历史记录，本次仅迁移并核对本地材料SHA256，没有重新执行仿真。证据索引和ExecPlan是可取得的叙述材料，原 ignored runs/、完整trace、原报告及二进制未取得。

```yaml
conditions_status: historical_incomplete
conditions_reason: 历史二进制与完整运行配置未归档，各probe参数曾变化，不能由统一信息重建每次运行环境。
source_repository: tonyhaohan/mcnf-sim-bridge
source_commit: 9e2058fcca7b95389d30e81cb0e52ffe03e2e930
source_issue: 3
config:
  bytes_per_directed_gpu_pair: 8000000
  bandwidth_gbps: 400
  packet_payload_bytes: 4096
  final_grid_N: [2, 4, 8, 16, 32]
  final_grid_M: [1, 2, 4, 8, 16]
  final_grid_Q: [1, 2, 4]
metric:
  theory_us: 8_000_000 * 8 * (N - 1) / (M * Q * 400_000_000_000) * 1_000_000
  gap: simulated_time / theoretical_time - 1
environment:
  simulator: ASTRA/ns-3 RDMA
  historical_binary_identity: null
```

原始要求第二条“N 在 1~16”保留在ExecPlan；历史Issue正文解释为M，不重写原话。各probe的具体参数以冻结ExecPlan为准，不能将0ns探针或lane-expanded语义混入默认条件。历史源码小型spike曾撤销，不能把“最终没有保留修改”写成“从未改过源码”。三项主张C003-01/C003-02/C003-03保留历史支持状态及可证伪条件，原始证据可获取性限制仍有效。迁移事件：EV003-IMPORT-20261002。

## I003-N01 Can native ASTRA reproduce the Clos N/M/Q target with realistic positive gap?

```yaml
provenance: user
timestamp: '2026-07-03T00:00:00+08:00'
overrides: {}
observations: []
claims: []
evidence:
- E003-01
```

### question

For N GPUs, M switches and Q equal-bandwidth GPU-switch links, can real ASTRA/ns-3 reproduce the 8MB all-to-all target divided by M and Q while retaining fixed protocol overhead and packet-tail effects?

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N01；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N02 A calibrated bridge estimate matches the target grid but is not simulator evidence

```yaml
provenance: ai-executed
timestamp: '2026-07-03T00:05:00+08:00'
overrides: {}
observations: []
claims: []
evidence:
- E003-02
```

### hypothesis

The theoretical denominator plus fixed protocol overhead, proportional overhead and packet-tail imbalance can provide a useful calibration baseline.

### method

Generate the N/M/Q grid with a bridge-side analytical estimate and compare it with the requested positive-gap band.

### result

The estimate matched the target grid, but it did not prove that ASTRA/ns-3 used the intended physical paths or parallel injection behavior.

### why_it_worked

The estimate directly encoded the target denominator and residual terms.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N02；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N03 Bundle solverPath does not control raw-rank ASTRA multi-lane injection

```yaml
provenance: ai-executed
timestamp: '2026-07-03T00:50:00+08:00'
overrides: {}
observations: []
claims:
- C003-01
evidence:
- E003-03
```

### hypothesis

Splitting a logical flow across solverPath entries in the bridge bundle will make real ASTRA use all M*Q physical lanes for the same GPU pair.

### method

Run raw-rank ASTRA probes for single-lane and multi-lane N/M/Q cases.

### result

Single-lane cases stayed close to theory, while M>1 or Q>1 cases remained near single-lane runtime.

### failure_mode

Chakra send/recv expresses rank-level communication; solverPath was metadata, not a route or QP binding contract honored by the ns-3 backend.

### lesson

A bridge path label cannot be treated as proof that packets follow that path.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N03；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N04 Lane-expanded ranks expose capacity but change the modeled system

```yaml
provenance: ai-executed
timestamp: '2026-07-03T01:20:00+08:00'
overrides:
  config.rank_representation: lane-expanded
observations: []
claims:
- C003-02
evidence:
- E003-04
```

### hypothesis

Representing each lane as an independent ASTRA rank can bypass the per-rank send gate and demonstrate the target M*Q injection capacity.

### method

Expand each original GPU into M*Q ASTRA ranks and run real matrices up to 2048 ranks.

### result

Many large-N cases reached the target, but the rank count and communication semantics no longer represented the original GPU cluster.

### lesson

This proxy is capacity evidence, not a credible replacement for raw GPU ranks.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N04；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N05 Narrow the calibration grid to powers of two

```yaml
provenance: user
timestamp: '2026-07-03T09:09:00+08:00'
overrides:
  config.grid_selection: powers_of_two
observations: []
claims: []
evidence:
- E003-01
- E003-04
```

### choice

Keep powers-of-two N, M and Q as the representative target instead of every integer in the original ranges.

### alternatives

- Complete all integer N/M/Q combinations.
- Keep only the earliest small probe matrix.

### why_it_worked

It retained the intended scale and parallelism regimes while reducing run cost.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N05；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N06 Can native RDMA QP and ECMP semantics meet the target without explicit routes?

```yaml
provenance: user
timestamp: '2026-07-03T14:00:00+08:00'
overrides: {}
observations: []
claims: []
evidence:
- E003-05
- E003-06
- E003-07
- E003-08
```

### question

Can 4KB packets, RDMA QPs, host QP hash, switch ECMP, egress round-robin and backend congestion-control parameters reproduce the target without a new explicit QP-to-path configuration interface?

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N06；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N07 Native all-to-all preserves standard semantics but misses M/Q scaling

```yaml
provenance: ai-executed
timestamp: '2026-07-03T14:40:00+08:00'
overrides:
  config.collective: native_all_to_all
observations: []
claims: []
evidence:
- E003-05
```

### hypothesis

ASTRA native all-to-all implementations will let the backend's RDMA and ECMP behavior naturally use all M*Q paths.

### result

M=1 direct cases were close to theory, but M>1 and Q>1 missed badly; ring and other native variants were slower or invalid for the target.

### failure_mode

Native collective and flow/QP-level ECMP did not spray each GPU pair across all intended lanes.

### lesson

Native all-to-all remains a protocol sanity probe, not the path-control solution.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N07；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N08 High-K QP hash striping improves throughput but is unstable and indirect

```yaml
provenance: ai-executed
timestamp: '2026-07-03T16:10:00+08:00'
overrides:
  config.qp_allocation: high_K_hash_striping
observations: []
claims:
- C003-03
evidence:
- E003-06
```

### hypothesis

Many independent RDMA sends per GPU pair will create enough QPs for host and switch hashes to approximate uniform use of the physical paths.

### method

Sweep stripe count K across representative N/M/Q cases and measure real ASTRA/ns-3 completion time.

### result

Selected cases reached the target, but results were non-monotonic, required tens or hundreds of QPs, and did not generalize across M and Q.

### lesson

High-K hashing is a diagnostic approximation, not an explicit or stable path contract.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N08；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N09 ECMP-visible topology exposes parallel links but still does not define paths

```yaml
provenance: ai-executed
timestamp: '2026-07-03T18:05:00+08:00'
overrides:
  config.topology: ecmp_visible_parallel_next_hops
observations: []
claims:
- C003-03
evidence:
- E003-07
```

### hypothesis

Replacing parallel links with distinct ECMP next-hop nodes will make Q visible to the unmodified backend and close the remaining gap.

### method

Export each parallel GPU-switch link through a distinct next-hop node and combine it with QP hash striping.

### result

Q became measurable and several cases improved, but hash-selected paths and small-N cases remained unstable or above the target.

### lesson

Making links hash-visible does not let a logical flow choose a named path group.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N09；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N10 Backend knobs and further hash tuning do not create a general route contract

```yaml
provenance: ai-executed
timestamp: '2026-07-03T19:40:00+08:00'
overrides:
  config.probe_family: backend_and_hash_parameter_search
observations: []
claims:
- C003-03
evidence:
- E003-08
```

### hypothesis

Congestion-control, queue, rendezvous, delay, source-port, seed or further K tuning can turn the high-K proxy into a general solution.

### result

Many knobs had no effect or regressed; isolated tuned points improved, but small-N cases and explicit path selection remained unresolved.

### failure_mode

Hash balance, QP overhead and fixed protocol cost changed together, while the bridge still could not state which complete physical path a QP must follow.

### lesson

Do not repeat broad parameter search when the missing capability is an explicit QP/path interface.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N10；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

## I003-N11 Replace the high-K proxy with explicit configuration-driven QP paths

```yaml
provenance: user-revised
timestamp: '2026-07-10T18:41:00+08:00'
overrides:
  config.target_interface: explicit_QP_groups_and_complete_paths
observations: []
claims:
- C003-03
evidence:
- E003-09
- E004-01
- E004-08
```

### result

This pivot became the Issue #6 simulator feature: explicit QP configuration, path-specific routes, persistent QP reuse and bridge-side 4KB message allocation.

### trigger

Issue #3 showed that implicit solverPath metadata, lane-expanded ranks and high-K hash tuning could not provide a small, auditable QP-to-path contract.

### new_direction

Let the bridge generate a small set of QPs, bind each QP to one complete physical path, group QPs per logical flow and configure the simulator with the fully resolved result.

### why_it_worked

It converted an opaque statistical approximation into a small inspectable contract while retaining the trusted RDMA data plane.

### 出处与边界

冻结 `migration/source/ara/trace/exploration_tree.yaml` 中 I003-N11；详细历史命令与变化见 `migration/source/issue3-ExecPlan.md`。本次未复跑；共用元数据中的 overrides仅表示已知差异；空映射不能推断历史没有差异。正文与冻结来源保留实际条件。

原Issue #6映射为本仓Issue #4；后继I004-N01由接收节点维护前置依赖，E004-01与E004-08由Issue4迁移记录提供。用户转向不作为新的科学实证。
