---
status: active
owner: core-maintainers
last_verified: 2026-09-17
scope: Issue19到ARA全局DAG的只读节点索引
---

# Issue #19

唯一事实源为`../trace/exploration_tree.yaml`，不另建研究图。

- `I019-N01`
- `I019-N02`
- `I019-N03`

入口为`I018-N03`；`I019-N02`同时依赖`I017-N03`，`I019-N03`同时依赖`I018-N03`。原物理模型问题`I017-N05`保持open。
