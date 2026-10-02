---
status: active
owner: core-maintainers
last_verified: 2026-07-12
scope: mcnf-sim-bridge 项目级 ARA artifact 入口
---

# MCNF Simulation Bridge ARA

本目录是整个 `mcnf-sim-bridge` 研究项目唯一的 ARA artifact。全局研究 DAG 位于 `trace/exploration_tree.yaml`；GitHub Issue 只作为 node 来源、session 边界和 `views/` 中的子图入口。

## Layer Index

- `logic/claims.md`：全局可证伪 claims 和开放问题。
- `src/artifacts.md`：代码、配置、测试和复现入口。
- `trace/exploration_tree.yaml`：唯一的全局研究 DAG。
- `trace/sessions/`：按研究 session 保存的结构化记录。
- `evidence/index.md`：全局 evidence id 与原始产物指针。
- `staging/observations.yaml`：尚未成熟为 node 或 claim 的观察。
- `views/`：Issue/主题到全局 node id 的只读索引。

## 全局 Idea 图

直接打开 [`views/global.html`](views/global.html) 可以查看所有 idea 及其关系；点击节点可查看完整内容。全局 DAG 更新后重新生成：

    python scripts/render_ara_graph.py

项目规范见 `docs/guideline/ara-research-protocol.md`。任何研究、实验、调参、设计评估或负结果整理开始前，先读取本文件、全局 DAG 和相关 view；结束前更新 ARA 并运行：

    PYTHONPATH=src python scripts/validate_ara.py
