---
status: active
owner: core-maintainers
last_verified: 2026-07-11
scope: 1MiB QP hash 与 round-robin 对照及默认策略选择
---

# Compare QP allocation policies and select the default

This ExecPlan is a living document maintained under `docs/guideline/PLAN.md`.

## Purpose / Big Picture

The existing bridge can assign each 4096B message to a QP either by deterministic hash or by round-robin, but the standard performance benchmark silently uses hash. This work makes both policies directly comparable on the same 1MiB N/M/Q/R cases, records simulated completion time and QP-load balance, and changes the default to round-robin only if real ASTRA ns-3 runs are stable and match the expected byte conservation and improved balance.

## User Raw Prompts

- “测试一下均匀分配和hash在1MB任务下gap能差多少？均匀分配肯定更均匀一些，如果这个功能稳定的话我们就把这个设为默认吧。”
- “好的，继续吧。另外我希望这样管理我们的编译产物：每次根据我们Astra代码库的某个sha值（类似于git commit号的前七位？）追加到编译产物名称后面，然后每次跑之前确认一下是否匹配的上，匹配不上就重新编译，能匹配则复用，你觉得可以吗？”
- “很好，把这部分内容提PR，然后我们继续对齐词汇。我感觉差不多了？还有要对齐的吗”

## Progress

- [x] (2026-07-11 23:21 CST) Created GitHub Issue #9 and linked branch `codex/9-round-robin-default` from `main`.
- [x] (2026-07-11 23:24 CST) Confirmed `scripts/generate_qp_bindings.py` already supports both `hash` and `round_robin`; no simulator change is needed.
- [x] (2026-07-11 23:29 CST) Added benchmark size/allocation parameters, policy-specific labels, configured/active QP counts, and per-flow QP message-count spread.
- [x] (2026-07-11 23:39 CST) Ran 12 paired real ASTRA ns-3 1MiB cases for hash and round-robin with shared binary and route calibration evidence.
- [x] (2026-07-11 23:43 CST) Switched the missing-field and standard benchmark default to round-robin; retained explicit hash and updated tests/docs.
- [x] (2026-07-11 23:44 CST) Completed 46-test full suite, focused allocator/benchmark tests, minimal bundle smoke, 24-row result audit, diff check, and strict self-review.
- [x] (2026-07-11 23:55 CST) Added ASTRA commit-addressed binary/runtime-library caching, automatic pre-run reuse/rebuild checks, full-SHA manifests, platform isolation, and a successful real cached-binary smoke without simulator source changes.
- [x] (2026-07-12 00:08 CST) Re-ran closeout validation: 50 Python tests, all seven minimal bundle smoke cases, diff check, clean ASTRA submodule, and linked-branch/PR-state checks passed.
- [x] (2026-07-12 00:10 CST) Committed `b84a64e`, pushed the linked branch, created PR #10 with a verified `Closes #9` relationship, and inspected initial reviewer output.
- [x] (2026-07-12 00:26 CST) Addressed macmini review P1 by caching and hashing protobuf runtime libraries beside the executable and ns-3 libraries; the old cache invalidated automatically, all 50 tests passed, and a real cached case again reproduced 23.648us.
- [x] (2026-07-12 00:35 CST) Addressed follow-up review P1 by removing the caller-provided protobuf directory from runtime lookup and centralizing environment construction so the verified cache always has precedence; also corrected the macOS protobuf-generation documentation.

## Surprises & Discoveries

- Observation: The current standard benchmark has a fixed `8_000_000` byte constant and identifies rows only by N/M/Q/R, so it cannot safely store hash and round-robin 1MiB results in one run root.
  Evidence: `scripts/run_clos_qp_benchmark.py` defines `SIZE_BYTES = 8_000_000`, omits `messageAllocation` from the generated performance plan, and therefore inherits the generator's hash default.

- Observation: At 1MiB, hash can leave a configured QP unused; the old benchmark incorrectly required one FCT row per configured QP.
  Evidence: `(N,M,Q,R)=(4,2,2,4)` used 382 of 384 configured QPs under hash but all 384 under round-robin. The corrected benchmark separately validates configured QPs, active QPs, FCT rows, and bytes.

- Observation: The vendored ns-3 provenance names upstream commit `f764bed`, but its tracked snapshot omits upstream `scratch/common.h`; the current AppleClang also needs compatibility build flags for old spdlog/fmt.
  Evidence: The real-run binary was built without source edits by supplying the exact upstream `scratch/common.h` from commit `f764bed` and local compiler compatibility flags. The submodule is clean after the build.

- Observation: Round-robin completed all 12 real cases with zero PFC and exact per-flow QP message counts; it reduced simulated completion time by 5.02% on average relative to hash.
  Evidence: `docs/plans/issue9_round_robin_default/allocation_comparison.md` and ignored raw results under `runs/issue9_1mib_allocation_compare/`.

- Observation: The ASTRA ns-3 executable dynamically links ns-3 and protobuf libraries outside the executable, so caching only the executable or only ns-3 libraries can load an incompatible protobuf ABI after an environment switch.
  Evidence: `otool -L` listed ten `libns3.42-*.dylib` dependencies and `libprotobuf.31.dylib`. Cache schema 2 copies and verifies both sets and prepends its SHA-specific library directory during execution.

- Observation: The SHA cache correctly rejected mixing a newly rebuilt binary with the existing 24-row comparison generated by the earlier binary.
  Evidence: `_validate_incremental_binary()` failed before simulation with the stale labels; a fresh `runs/issue9_sha_cache_smoke` completed successfully with the cached binary and cached runtime libraries.

## Decision Log

- Decision: Reuse the existing `messageAllocation` contract and add no new allocator or simulator behavior.
  Rationale: The requested comparison and possible default change are entirely bridge-side; modifying ASTRA or ns-3 would add risk without capability.
  Date/Author: 2026-07-11 / Codex local.

- Decision: Interpret “1MB” as 1 MiB (`1_048_576` bytes), matching the repository's existing `1mib` standard smoke naming.
  Rationale: This produces exactly 256 messages of 4096B and avoids a partial tail message, making load-balance comparison unambiguous.
  Date/Author: 2026-07-11 / Codex local.

- Decision: Promote round-robin to the default while preserving `messageAllocation: "hash"` as an explicit option.
  Rationale: Round-robin was stable in all paired cases, made the QP message-count spread exactly zero, used every configured QP, and was never slower than hash in this grid.
  Date/Author: 2026-07-11 / Codex local.

- Decision: Migrate legacy benchmark summaries in memory as explicit hash rows instead of rejecting or silently treating them as the new default.
  Rationale: Existing Issue #6 results predate the policy field and were generated with hash; preserving that meaning prevents mixed-policy reports and keeps old run roots reusable.
  Date/Author: 2026-07-11 / Codex local.

- Decision: Name the executable with the first seven ASTRA commit characters, but validate the full commit in a manifest and isolate caches by OS/CPU architecture.
  Rationale: The short SHA keeps names readable; full SHA, binary/library hashes, and platform fields prevent accidental collision or cross-platform reuse.
  Date/Author: 2026-07-11 / Codex local.

- Decision: Refuse commit-cache reuse when the ASTRA worktree is dirty.
  Rationale: A commit name cannot identify uncommitted source content, so caching it under the clean commit SHA would make experiment provenance false.
  Date/Author: 2026-07-11 / Codex local.

## Outcomes & Retrospective

The paired real comparison is complete and supports round-robin as the default. Across 12 pairs, round-robin changed simulated time by 0.00% to -8.90% relative to hash, with an average -5.02%; its mean theory gap was 16.35% versus hash's 22.77%. The ASTRA SHA cache now preserves the executable and matching ns-3 and protobuf dynamic libraries, and a real cached-binary case reproduced 23.648us after the schema-2 rebuild. The final suite passed 50 tests with three existing protobuf deprecation warnings; Python compilation, diff checks, minimal bundle smoke, automatic macOS rebuild, cache-hit reuse, and the real cached-binary run also passed. Strict self-review found no blocking issue. The residual validation gap is a clean Linux rebuild and repeat, which remains the repository's paper-grade archive gate rather than a blocker for this bridge-side default change.

## Context and Orientation

`scripts/generate_qp_bindings.py` performs QP selection. For hash it computes BLAKE2s over `(hashSeed, flowId, messageIndex)`; for round-robin it chooses `members[messageIndex % groupSize]`. `scripts/run_clos_qp_benchmark.py` builds the standard N/M/Q/R topology and QP plan, compiles Chakra ET, invokes ASTRA ns-3, and writes JSON/CSV/Markdown summaries. `tests/test_qp_bindings.py` checks allocator semantics, while `tests/test_clos_qp_benchmark.py` checks the reusable benchmark contract.

## Plan of Work

Make the standard benchmark accept `--size-bytes` and `--message-allocation`, include both values in row labels and summaries, and compute per-flow QP message-count spread from the already generated child sends. Use one explicit `DEFAULT_MESSAGE_ALLOCATION` constant as the bridge default. Initially run paired experiments with explicit `hash` and `round_robin`; only after evidence is collected set that constant and `generate_qp_bindings.py`'s missing-field fallback to `round_robin`.

Use a representative coarse set containing Q=1 and Q>1, multiple physical paths, and multiple QPs per path. Each pair must use the same topology, R, flow size, binary, and QP definitions. Compare simulation time, relative theory gap, host success, PFC count, FCT byte conservation, configured/active QPs, and maximum per-flow QP message-count spread.

## Concrete Steps

From `/private/tmp/mcnf-sim-bridge-issue9`, run focused tests with `PYTHONPATH=src pytest -q tests/test_qp_bindings.py tests/test_clos_qp_benchmark.py`. Build ASTRA ns-3 in the pinned submodule using the repository build entry under the `math` conda environment. Run paired 1MiB cases into separate ignored `runs/` roots, then aggregate their `summary.json` rows into the issue plan directory only as a concise Markdown result and machine-readable JSON if the result is stable.

## Validation and Acceptance

Both allocation policies must complete all selected real cases with zero UDP drop, conserved bytes, matching binary hash, and no unexplained PFC difference. Round-robin must have QP message-count spread no worse than hash and should be exactly zero whenever 256 messages divide the QP-group size. The simulated completion-time difference must be reported rather than assumed. If those conditions hold, plans omitting `messageAllocation` must resolve to round-robin, while explicit hash plans remain deterministic and valid. Run `PYTHONPATH=src pytest -q` and `git diff --check` after the change.

## Idempotence and Recovery

All experiment artifacts live under ignored `runs/` paths and can be regenerated with `--force`. Labels include size and allocation policy, so hash and round-robin safely coexist in one run root and an interrupted run cannot overwrite the other policy. No ASTRA or ns-3 source is edited.

## Artifacts and Notes

GitHub issue: https://github.com/tonyhaohan/mcnf-sim-bridge/issues/9

Durable result: `docs/plans/issue9_round_robin_default/allocation_comparison.md`.

Raw result: `runs/issue9_1mib_allocation_compare/summary.json` with 24 successful real rows.

## Interfaces and Dependencies

The public QP plan field remains `messageAllocation` with accepted values `hash` and `round_robin`. The benchmark CLI adds only integer `--size-bytes` and the same two-valued `--message-allocation`. No dependency is added.

Revision note 2026-07-11 / Codex local: created the plan after inspecting the current allocator and benchmark, before implementation or experiment execution.

Revision note 2026-07-11 / Codex local: recorded the completed paired experiment, the active-QP discovery, the default-policy decision, and build evidence.

Revision note 2026-07-11 / Codex local: recorded legacy-summary compatibility, final validation, and self-review outcome.

Revision note 2026-07-11 / Codex local: added the user's ASTRA SHA-addressed build-artifact requirement and reopened implementation.

Revision note 2026-07-11 / Codex local: recorded executable/runtime-library cache implementation, full-SHA safety decisions, and real cache smoke evidence.

Revision note 2026-07-12 / Codex local: recorded final PR closeout validation and remaining delivery steps.

Revision note 2026-07-12 / Codex local: recorded commit/push/PR delivery, verified Issue #9 closing linkage, and captured the initial review state.
