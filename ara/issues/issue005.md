# Issue #5 — QP均匀分配、构建缓存与单层Clos差距诊断


## 统一信息


这是源 Issue #9 的历史迁移。2026-10-02 只转换记录和核验归档文本身份，没有重新仿真、下载原始trace或验证历史远端。源仓冻结提交 9e2058fcca7b95389d30e81cb0e52ffe03e2e930；所有 historical accepted 保留为 idea accepted，并非迁移证明科学成立。后续 Issue #14 及以后的成果不纳入本 Issue。

```yaml
source_repository: tonyhaohan/mcnf-sim-bridge
source_issue: 9
source_commit: 9e2058fcca7b95389d30e81cb0e52ffe03e2e930
conditions_status: historical_incomplete
conditions_reason: 源节点跨macOS/Linux和多批实验；完整公共环境、配置、源码overlay与原raw未随冻结源提供
conditions: 已知1MiB=1048576B与8MB=8000000B不能混用；实际方法与差异在各章节
raw_runs: unavailable
```

来源入口：migration/source/ara/trace/exploration_tree.yaml、migration/source/ara/evidence/index.md。完整原始图保存在冻结源；本纪要只按固定字段保存正文，不再复制旧边字段。overrides只列已知差异；空映射不表示历史没有其他差异。


## I005-N01 Should uniform allocation replace hash as the default?

```yaml
source_node: I009-N01
timestamp: '2026-07-11T23:21:00+08:00'
overrides: {}
evidence:
- E005-01
```

### question

For a 1MiB logical flow over the same QP group, how much do hash and round-robin differ in balance and simulation time, and is round-robin stable enough to become the default?

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N02 Run paired 1MiB hash and round-robin cases

```yaml
source_node: I009-N02
timestamp: '2026-07-11T23:39:00+08:00'
overrides:
  config.bytes_per_pair: 1048576
  config.packet_bytes: 4096
  config.R:
  - 1
  - 2
  - 4
evidence:
- E005-02
```

### hypothesis

Round-robin should reduce QP load dispersion and should not make completion time worse when paths and QPs are held constant.

### method

Use four representative N/M/Q topologies and R=1,2,4. Hold binary, complete paths, QPs and trace calibration constant across each policy pair.

### result

All 24 real runs completed with zero PFC and conserved bytes/FCT. Round-robin was never slower and improved mean completion time by 5.02%.

### why_it_worked

Pairing changes only 4KB-packet QP selection, isolating the allocation policy.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N03 Measure active QPs and per-flow message-count spread

```yaml
source_node: I009-N03
timestamp: '2026-07-11T23:43:00+08:00'
overrides:
  config.bytes_per_pair: 1048576
  config.packet_bytes: 4096
  config.R:
  - 1
  - 2
  - 4
evidence:
- E005-03
```

### hypothesis

Hash can leave configured QPs unused and produce visible per-flow imbalance even when the same group supports exact uniform allocation.

### method

Separate configured QPs, active QPs and FCT rows, and compute the maximum per-flow QP message-count difference.

### result

Hash spread reached 32 and left two of 384 QPs unused in one case; round-robin spread was zero in every tested group.

### why_it_worked

The metric observes actual packet assignment instead of assuming configured QPs all carry traffic.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N04 Make uniform allocation the default and retain explicit hash

```yaml
source_node: I009-N04
timestamp: '2026-07-11T23:43:00+08:00'
overrides:
  config.bytes_per_pair: 1048576
  config.packet_bytes: 4096
  config.R:
  - 1
  - 2
  - 4
evidence:
- E005-02
- E005-03
- E005-04
```

### choice

Plans without messageAllocation and the standard benchmark use round_robin; messageAllocation=hash remains deterministic and supported.

### alternatives

- Keep hash as the default.
- Remove hash entirely.

### why_it_worked

Uniform allocation met stability, balance and performance criteria while preserving hash as a controlled comparison.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N05 Preserve legacy hash rows and distinguish active QPs

```yaml
source_node: I009-N05
timestamp: '2026-07-11T23:44:00+08:00'
overrides:
  config.bytes_per_pair: 1048576
  config.packet_bytes: 4096
  config.R:
  - 1
  - 2
  - 4
evidence:
- E005-03
- E005-04
```

### choice

Interpret summaries without allocation metadata as hash rows and record configured QPs, active QPs and FCT rows separately in new summaries.

### alternatives

- Apply the new default retroactively to old rows.
- Reject every old run root.

### why_it_worked

Historical evidence keeps its original meaning after the default changes.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，新默认决定直接导致保护旧hash行语义的需求。


## I005-N06 Can ASTRA build artifacts be safely reused by commit SHA?

```yaml
source_node: I009-N06
timestamp: '2026-07-11T23:48:00+08:00'
overrides: {}
evidence:
- E005-05
```

### question

Can compiled artifact names contain the first seven ASTRA commit characters, reuse a matching build before each run, and rebuild on mismatch without compromising runtime provenance?

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N07 Caching only the executable or ns-3 libraries is not ABI-safe

```yaml
source_node: I009-N07
timestamp: '2026-07-12T00:26:00+08:00'
overrides: {}
evidence:
- E005-06
```

### hypothesis

A source-addressed executable plus matching ns-3 libraries may be sufficient for safe reuse.

### result

The binary also depends on protobuf, and an external protobuf path could be loaded before the cached copy.

### failure_mode

The cache verified fewer artifacts than the dynamic loader actually used.

### lesson

Reproducibility requires the runtime dependency set and loader precedence, not just a filename containing a source SHA.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N08 Bind binary and runtime libraries in one verified cache

```yaml
source_node: I009-N08
timestamp: '2026-07-12T00:26:00+08:00'
overrides: {}
evidence:
- E005-07
- E005-08
```

### trigger

Review and dynamic dependency inspection showed protobuf was outside the original verified cache set.

### new_direction

Cache ns-3 and protobuf libraries beside the binary, record their hashes with full ASTRA SHA and platform metadata, and invalidate schema-1 caches.

### result

Cache schema 2 rebuilds incomplete entries and validates every artifact.

### why_it_worked

The cache becomes a self-contained binary/runtime set identified by source and verified by content.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N09 External protobuf path precedence bypasses the verified cache

```yaml
source_node: I009-N09
timestamp: '2026-07-12T00:35:00+08:00'
overrides: {}
evidence:
- E005-06
```

### hypothesis

The caller-provided protobuf directory can remain in the runtime loader path after a verified protobuf copy is cached.

### result

Follow-up review showed both real-run paths put the external directory ahead of the verified cache.

### failure_mode

Loader order selected an unverified ABI despite the presence of a hashed copy.

### lesson

The caller protobuf path is build-time input only. Runtime loading must use a shared helper that prepends the verified cache ahead of ambient paths.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，已建立verified cache后，外部protobuf优先级才构成具体绕过该cache的问题。


## I005-N10 Accept the uniform default and verified SHA cache

```yaml
source_node: I009-N10
timestamp: '2026-07-12T10:35:00+08:00'
overrides: {}
evidence:
- E005-08
- E005-09
```

### choice

Adopt uniform allocation as default, retain explicit hash, preserve legacy row semantics, and use the full binary/runtime cache after review fixes.

### alternatives

- Keep hash as default and omit cache provenance.
- Accept executable-only cache validation.

### why_it_worked

Focused tests, paired real experiments, a real cache-hit run and repeated review checked behavior and provenance.

### known_limits

Clean Linux rebuild and formal rerun remain paper-grade archive work.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N11 Uniform allocation keeps all four tested 8MB R=1 Linux Clos gaps below eight percent

```yaml
source_node: I009-N11
timestamp: '2026-09-15T19:15:00+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-10
```

### hypothesis

Uniform packet allocation improves or preserves time compared with hash for the same four 8MB R=1 configurations.

### method

Pair hash and round_robin with identical physical topology, network settings, QPs, paths and binary; run twice.

### result

Uniform times are 166.208, 85.119, 249.999 and 127.660us; ideal-time gaps are 3.88%, 6.39875%, 4.16625% and 6.38333%; all repeats agree.

### why_it_worked

The measured QP message-count spread is at most one; paired checks isolate allocation while retaining RDMA behavior.

### known_limits

Only four R=1 8MB configurations; no general claim for all Clos sizes, 1MiB, Allreduce or real hardware.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N12 Fixed-version single-layer Clos scales reproducibly through selected 32-card cases

```yaml
source_node: I009-N12
timestamp: '2026-09-16T11:11:16+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-11
- E005-12
```

### hypothesis

The frozen uniform-allocation implementation remains verifiable on larger representative single-layer Clos configurations.

### method

Run N=8/16/32 with M=2 and Q=1/2, then N=8/16 with M=4 and Q=1/2 plus 8/2/4; retain R=1, 8MB, 400Gbps and repeat each configuration.

### result

All 22 runs across 11 configurations pass input/FCT/native-calibration audits and repeat to the nanosecond; gaps range 2.9975%-8.367142857%, with 10 of 11 below 8%.

### why_it_worked

Existing explicit paths and uniform allocation are reused without simulator or network-parameter changes; actual qp_config and per-child FCT are independently checked.

### known_limits

This is not all 225 combinations or real solver Allreduce; 8/2/4 exceeds the 8% direction and 32/2/2 has PFC records, so low-gap and no-congestion claims do not generalize.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，四个Linux基础配置的可复现验证是扩规模实验主要知识前提；wrapper失败保留为并列依赖。


## I005-N13 What explains the high-parallelism residual gap and the separate 32-card PFC observation?

```yaml
source_node: I009-N13
timestamp: '2026-09-16T11:11:16+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-11
- E005-12
```

### question

Why does 8/2/4 take 151.714us versus 148.855us for equal ideal-capacity 8/4/2, and what completion-time contribution does 32/2/2 PFC have? These are separate observations until causally tested.

### lesson

Subsequent trace and controlled route completion identify ACK concentration, but do not isolate the portion of 32-card latency caused by PFC alone.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N14 Consolidate current Clos gaps and failures before expanding scope

```yaml
source_node: I009-N14
timestamp: '2026-09-16T11:24:00+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-13
```

### choice

Pause solver connection and new topologies; diagnose larger residual gaps, test justified improvements, and verify recovery of recent failed batches.

### alternatives

- Proceed immediately to real NodeArcResult and double-layer Clos.
- Hide high-gap rows or change the theoretical denominator.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N15 Full performance traces identify concentrated ACK return paths as a bottleneck

```yaml
source_node: I009-N15
timestamp: '2026-09-16T11:33:00+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-14
```

### hypothesis

Native default routing drops parallel-interface candidates for ACK destinations while explicit forward aliases retain full paths.

### method

Inspect the actual build header, repeat two 8MB cases with trace off/on, audit complete packet sequences and per-directed-port serialization, and perform 4/16MB size diagnostics.

### result

Trace preserves original151714/148855ns times. Each full trace contains448000000 unique payload bytes. ACK uses32/128 directed ports for Q4 and64/128 for Q2. Busiest modeled serialization is149643/146773ns, a2870ns difference versus2859ns observed. Actual common.h stores only the last interface per neighbor.

### why_it_worked

Actual packet evidence and source structure agree; payload, headers, ACK work and per-link idle are separated without changing the ideal denominator.

### known_limits

Packet serialization is the current nanosecond model, not a full hardware Ethernet accounting; port intervals cannot be added across links.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N16 Completing missing ACK parallel routes improves isolated cases without changing forward traffic or protocol settings

```yaml
source_node: I009-N16
timestamp: '2026-09-16T11:40:00+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-15
```

### hypothesis

Append only omitted ordinary-destination interface candidates in an isolated qp_config while preserving forward paths, QPs, payload, ACK/PFC and physical parameters.

### method

Run8/2/4,8/4/2,8/2/1 and32/2/2 twice; Q1 is a true no-op control, two target repeats record full traces. Independently reconstruct added routes and validate FCT, rank completion, ET files and trace conservation.

### result

Times are147292,147006,579554,1280798ns with exact repeats; gaps5.20857%,5.00429%,3.49179%,3.29016%. All21472 FCT records and224 ET/input files pass. Target ACK coverage becomes128/128 directed ports with unchanged data loads and ACK totals.32-card PFC falls from312 records to0.

### why_it_worked

Native hashing can use all existing shortest-path parallel interfaces for ACK return traffic instead of only the last link per neighbor.

### known_limits

Candidate input only, no merged/default implementation or simulator source change. Four configurations, R1,8MB only;32-card no-retransmission and PFC-only latency contribution are not established.

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。


## I005-N17 How should ACK route completion be integrated and validated beyond this prototype?

```yaml
source_node: I009-N17
timestamp: '2026-09-16T11:40:00+08:00'
overrides:
  config.bytes_per_pair: 8000000
  config.packet_bytes: 4096
  config.R: 1
  config.link_bandwidth_gbps: 400
  config.link_latency_ns: 500
  environment.platform: Linux
evidence:
- E005-14
- E005-15
```

### question

Can an explicit bridge option safely detect the default-route assumption and preserve existing behavior across more single-layer configurations, while separating remaining protocol/discretization costs and PFC-only latency?

### limitations

冻结源正文；本次未重跑。完整配置/环境和raw可获取性见关联证据，未保存条件不作相同条件假定。

### migration

EV005-import-20261002记录导入；主要依赖是迁移索引判断，保留最能解释当前来由的主链前置；并列依赖全部保留。
