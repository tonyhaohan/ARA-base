# ARA Base

研究、实验、设计评估、负结果整理与收尾，读取 `.agents/skills/ara-research-manager/SKILL.md` 和 `docs/PROTOCOL.md`，按需读取 `docs/NOTES.md`。

- 用户要求高于本仓流程默认。保留历史原话、失败和不确定性，不把推测写成已验证事实。
- 每个研究 Issue 对应唯一 linked branch 和 ExecPlan；分支 `codex/issueNNN-topic`。main 是集成分支。
- ExecPlan 位于 `docs/plans/issueNNN_topic/ExecPlan.md`。一个 Issue 始终只维护一份；逐字追加 User Raw Prompts。进展、下一步、决定、证据、产物和恢复说明按时间追加，取代旧决定时标出引用。目标可更新，历史不可重写。
- 使用 `scripts/ara.py` 按需读取记录，不默认把全体 idea 正文加载进上下文。
- 本地修改后执行 `validate`、测试和 `render`；交付前检查生成页面是否最新。需要 GitHub 真实性时执行 `validate --github`。
- 新仓库的 main 是可继承的空起点。基准自身的工程执行计划不注入默认研究 artifact；研究数据放在明确的研究分支或示例中。
- GitHub 读写优先 gh CLI；Issue 内容中文，原始用户内容不覆盖。只进行用户请求所授权的外部写入、发布、提交和合并。
