---
status: archived
owner: codex-local
last_verified: 2026-09-16
scope: 本项目已完成Issue6/9的只读原始叙事证据，不是第二张研究图或活跃执行计划
---

# 已完成实验的原始证据文档

这六份Markdown在PR15中从 `docs/plans/` 等内容搬迁至此；它们来自本项目的前置复现、扩规模和失败诊断，不是MCNF_full或旧仿真器迁移。`docs/plans/issue14_clos_return_routes/ExecPlan.md` 仍是本任务的活跃执行契约。

- `issue6_linux_clos_reproduction/ExecPlan.md`、`RESULTS.md`
- `issue6_linux_clos_scaling/ExecPlan.md`、`RESULTS.md`
- `issue9_clos_gap_diagnosis/ExecPlan.md`、`RESULTS.md`

内容按搬迁前提交 `96ba0f953040ef0a1be6792f73aea24ae4827beb` 保留，包括失败、当时的未完成项和当时路径。旧路径若出现在历史叙事中表示当时操作位置，不代表新增活跃计划。现行证据索引和session指针已更新；原本地脏工作区与服务器原始输入/trace未移动或删除。

这些文件是全局ARA的支撑证据，不单独维护研究状态。唯一研究图仍是 `ara/trace/exploration_tree.yaml`，最新主张/限制以对应node、`ara/evidence/index.md`和`ara/logic/claims.md`为准。本次是机械归档治理，不新增实验或科学结论。
