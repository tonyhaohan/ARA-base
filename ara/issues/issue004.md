# Issue #4 — 配置驱动的 RDMA QP 历史研究

## 统一信息

来源：原 [Issue #6](https://github.com/tonyhaohan/mcnf-sim-bridge/issues/6)，冻结提交 `9e2058fcca7b95389d30e81cb0e52ffe03e2e930`。本次只迁移15个I006起源节点，历史时间保留；2026-10-02仅执行记录迁移，未运行仿真。旧next反转为depends_on，also_depends_on合并；primary_dependency按研究来由选择，属迁移判断；多父节点选择依据见audit.md。跨Issue引用按mapping转换。

```yaml
conditions_status: historical_incomplete
conditions_reason: 源记录未保存全部实验环境、原始输入及历史构建身份；下面仅列标准粗扫已知条件，不推断其他idea使用相同配置。
config:
  bytes_per_ordered_pair: 8000000
  message_bytes: 4096
  N: GPU数
  M: switch数
  Q: 每个GPU-switch pair平行链路数
  R: 每条完整路径QP数
  endpoint_group_size: M*Q^2*R
  theory_us: 160*(N-1)/(M*Q)
source_commit: 9e2058fcca7b95389d30e81cb0e52ffe03e2e930
```

这些共享条件只用于标准粗扫；原型/reuse/后续Linux覆盖写在各节点。历史opening最初不实现persistent reuse且使用source-port preimage，最终已转为alias及reuse；保留原文而不把最终范围倒写为opening。声明C004-01/03是接口/语义判断，标hypothesis；C004-02/04仅有限历史报告支持。唯一未解决观察 O004-20260915-historical-hash-microdifference 关联I004-N13。导入事件 EV004-import-01。所有完整原节点内容见冻结源DAG，以下逐字段保留正文。

## I004-N01 Can a small explicit QP group express solver-selected paths credibly?

```yaml
source_id: I006-N01
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-10T18:41:00+08:00'
overrides: {}
evidence:
- E004-01
```

### question

Can each logical flow choose from a user-defined QP group, with every QP fixed to one complete shortest physical path and every 4KB packet choosing a QP once, without replacing native RDMA behavior?


### 迁移边界

原记录 I006-N01（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N02 High-K automatic QP hash cannot serve as the path contract

```yaml
source_id: I006-N02
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-10T18:41:00+08:00'
overrides: {}
evidence:
- E004-02
```

### hypothesis

Creating 100 or more QPs and relying on automatic host/switch hashes might produce enough balance to stand in for explicit QP placement.

### result

The approach requires excessive QPs, hides the actual binding, and cannot express a flow-specific path group or QP group.

### failure_mode

Statistical hash collisions replace the requested path contract and make balance depend on a large, opaque QP population.

### lesson

QP placement and 4KB-packet QP selection must be explicit bridge contracts, not consequences of a large hash population.


### 迁移边界

原记录 I006-N02（rejected）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N03 Put QP plans and packet allocation in the bridge

```yaml
source_id: I006-N03
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-10T18:41:00+08:00'
overrides: {}
evidence:
- E004-01
```

### choice

The bridge defines paths, QPs, QP groups, flow-to-group mappings and 4KB-packet allocation. The simulator reads only resolved configuration.

### alternatives

- Let the simulator search or generate QPs automatically.
- Replace switch forwarding behavior with a new path selector.

### why_it_worked

Policy and validation stay in auditable interface code while the trusted RDMA data plane remains intact.


### 迁移边界

原记录 I006-N03（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N04 Source-port preimage and route-slot manifests form a useful prototype

```yaml
source_id: I006-N04
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-10T21:20:00+08:00'
overrides: {}
evidence:
- E004-03
```

### hypothesis

Source ports whose hashes hit calibrated route slots might provide the explicit path binding needed by the bridge.

### method

Search source ports for target route slots and calibrate slot-to-interface mapping with native trace.

### result

Key cases and a five-path 3+2 grouping worked, but route-slot order depended on topology/build iteration order and was not a stable complete-path ABI.

### lesson

Hash preimages are useful diagnostics, but a credible path contract must name physical edges and must not depend on route-vector order.


### 迁移边界

原记录 I006-N04（superseded）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N05 Use path-specific destination aliases and one output per hop

```yaml
source_id: I006-N05
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-11T19:22:00+08:00'
overrides: {}
evidence:
- E004-04
```

### trigger

The source-port prototype could not provide a stable complete-path ABI.

### new_direction

Allocate a destination alias for each complete path and register exactly one output interface for that alias at every hop.

### result

All four Q=2 complete paths and both directions matched the configured physical interfaces in native trace without changing switch hashing.

### why_it_worked

Native forwarding hashes only when a destination has multiple outputs; a path-specific alias makes the candidate set size one at every hop.


### 迁移边界

原记录 I006-N05（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N06 Persistent QP FIFO preserves connection-level state

```yaml
source_id: I006-N06
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-11T19:24:00+08:00'
overrides: {}
evidence:
- E004-05
```

### hypothesis

Retaining a configured QP and queueing later sends should reproduce the connection-lifetime behavior missing from temporary per-send QPs.

### method

Send two consecutive 1MiB messages using the same configured QP and inspect sequence continuation and completion behavior.

### result

The second message queued behind the first and continued the same sequence and congestion-control state.

### why_it_worked

The adapter retains the QP after message completion and advances its sequence space instead of invoking temporary-QP teardown.


### 迁移边界

原记录 I006-N06（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N07 An external public ns-3 PR is the wrong repository boundary

```yaml
source_id: I006-N07
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-11T01:07:00+08:00'
overrides: {}
evidence:
- E004-07
```

### hypothesis

The minimal backend change should be contributed directly to the public astra-network-ns3 repository.

### result

The project did not own a private counterpart there, so the PR was withdrawn and the dependency chain was paused.

### failure_mode

The proposed delivery changed a repository outside the user's ownership and split a small private simulator modification across unnecessary repositories.

### lesson

Simulator changes must stay in repositories the project owns; nested ns-3 can remain inside the private ASTRA repository.


### 迁移边界

原记录 I006-N07（rejected）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N08 Sweep one, two and four QPs per complete path

```yaml
source_id: I006-N08
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-11T19:29:00+08:00'
overrides: {}
evidence:
- E004-06
```

### hypothesis

More than one QP per complete path might improve capacity or stability.

### method

Run representative N/M/Q topologies with R=1,2,4 using the same path calibration and compare simulation time, theory gap and PFC events.

### result

All 12 final cases succeeded; R changed completion time by at most 0.79% relative to R=1 and produced no stable capacity gain.

### why_it_worked

The experiment isolates QP multiplicity while holding physical capacity and path definitions constant.


### 迁移边界

原记录 I006-N08（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N09 Default to one QP per complete physical path

```yaml
source_id: I006-N09
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-11T19:29:00+08:00'
overrides: {}
evidence:
- E004-06
```

### choice

Use R=1 as the default; retain R=2 and R=4 as benchmark dimensions rather than assumed performance improvements.

### alternatives

- Add multiple QPs per path by default.
- Tune R independently for every topology.

### why_it_worked

It is the smallest configuration consistent with measured capacity and avoids recreating the excessive-QP complexity.


### 迁移边界

原记录 I006-N09（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N10 Accept the minimal configuration-driven persistent-QP adapter

```yaml
source_id: I006-N10
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-07-11T21:52:00+08:00'
overrides: {}
evidence:
- E004-08
- E004-09
```

### choice

Adopt the merged resolved-QP interface, complete-path aliases, persistent QP FIFO and standard benchmark as the new simulator foundation.

### alternatives

- Continue the Issue
- Expand simulator core routing behavior.

### why_it_worked

Policy remains in the bridge, adapter changes are narrow, nested ns-3 changes only persistent completion behavior, and native traces check complete paths.

### known_limits

Clean Linux build and paper-grade rerun remain open archive work.


### 迁移边界

原记录 I006-N10（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N11 Forced policy runs in a shared directory overwrite earlier trace evidence

```yaml
source_id: I006-N11
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-09-15T19:09:00+08:00'
overrides: {}
evidence:
- E004-10
```

### hypothesis

Shared run-root labels can retain both policy rows and all calibration evidence under force.
### result

All performance values repeated, but eight hash rows referenced calibration traces overwritten by later runs.
### failure_mode

_calibrate(force=True) overwrites a topology trace while prior summary rows retain its former SHA256.
### lesson

Stable simulated time does not establish archive integrity; keep each policy and pass in its own run-root.

### 迁移边界

原记录 I006-N11（rejected）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N12 Isolate policy and pass output directories without changing simulator behavior

```yaml
source_id: I006-N12
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-09-15T19:11:00+08:00'
overrides: {}
evidence:
- E004-11
```

### trigger

Shared force-run calibration evidence failed the independent checksum audit.
### new_direction

Use first/hash, first/round_robin, repeat/hash and repeat/round_robin in a new experiment directory.
### result

All 16 result references match retained raw evidence; independent parsing verifies 520 QP paths.
### why_it_worked

Each policy/pass owns the calibration files referenced by its results; no historical hashes are rewritten.

### 迁移边界

原记录 I006-N12（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N13 Reproduce four R=1 8MB Clos hash cases on clean Linux-built ASTRA

```yaml
source_id: I006-N13
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-09-15T19:15:00+08:00'
overrides: {}
evidence:
- E004-11
```

### hypothesis

The four historical R=1 Clos cases remain numerically close after a Linux build with unchanged model settings.
### method

Run N/M/Q 2/1/1, 2/1/2, 4/2/1 and 4/2/2 with 8000000 bytes per ordered pair, 400Gbps and explicit hash; repeat.
### result

Hash times are 166.208, 86.826, 255.114 and 131.030us; repeat times are identical and maximum historical deviation is 0.1843%.
### lesson

This is approximate historical reproduction of four R=1 cases, not exact cross-build equality or complete R=2/4 and full-grid archival coverage.

### 迁移边界

原记录 I006-N13（partial）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N14 Wrapper validation must follow the actual benchmark summary schema

```yaml
source_id: I006-N14
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-09-16T11:00:03+08:00'
overrides: {}
evidence:
- E004-12
```

### hypothesis

The scaling wrapper can validate each successful row through a size_bytes field.
### result

The first eight-card simulation completed, but the wrapper raised KeyError because the field is size_bytes_per_pair.
### failure_mode

An assumed output key stopped the batch after one simulator run; it was not a simulator failure.
### lesson

Check wrapper assumptions against retained baseline artifacts; preserve the failed batch and rerun into a new directory after a wrapper-only fix.

### 迁移边界

原记录 I006-N14（rejected）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。

## I004-N15 Verify that both recent wrapper or archive failures have successful same-input recovery

```yaml
source_id: I006-N15
source: migration/source/ara/trace/exploration_tree.yaml
timestamp: '2026-09-16T11:30:00+08:00'
overrides: {}
evidence:
- E004-13
```

### hypothesis

The recent failed batches reflect experiment tooling faults rather than unfinishable network configurations.
### method

Compare failed and successful wrappers, raw summaries, trace references and input/FCT hashes without rewriting failed evidence.
### result

The archive-overwrite batch had 16 successful simulations but 8 stale hash trace references; isolated reruns restore all references and preserve 80 input/FCT file hashes. The field-name failure has a successful 579554ns simulation; its corrected 12-run batch preserves the first case's five key hashes and succeeds.

### 迁移边界

原记录 I006-N15（accepted）在本次导入中保留；未新验证，其证据为报告记录，原运行产物未取得。
