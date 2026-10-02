# 首次读取者实际验收

2026-10-02。仅按 AGENTS、README 及其直接引用的 research-manager skill、PROTOCOL、NOTES 操作。未读取程序实现，未重跑历史仿真，未使用 Git 或访问远端。

## 入口与环境

实际运行 `cat AGENTS.md README.md`，再读 `.agents/skills/ara-research-manager/SKILL.md docs/PROTOCOL.md docs/NOTES.md`。
`ls -ld .venv .work` 确认已有环境，`.venv/bin/python scripts/ara.py --help` 成功；复用现有 .venv，没有重新安装依赖。

## 实际查询

- `.venv/bin/python scripts/ara.py issues`：成功，当前研究 Issue 为 #3「Clos all-to-all 历史校准与显式路径契约的失败路线」、#4「历史迁移：配置驱动的 RDMA QP 绑定与 bridge 侧分组」、#5「历史迁移：QP均匀分配、构建缓存与单层Clos差距诊断」，输出 outcome 均为 partial。
- `.venv/bin/python scripts/ara.py ideas --issue 5`：成功，列出 I005-N01 至 I005-N17 共 17 个节点。
- `cat ara/issues/issue005.yaml`：按 PROTOCOL 的文件归属找到重点列表。best_ideas 为 I005-N02（12组/24次成功配对，平均快5.02%，有限覆盖）及 I005-N16（四配置重复、Q1负对照、输入不变检查支持ACK补全候选，尚未集成）；promising_ideas 为 I005-N17（正式受限选项和更广回归，协议开销/PFC贡献待检验）。这是仓库归纳，不是本次重新评判实验。
- `.venv/bin/python scripts/ara.py read I005-N17`：成功，仅得到 Issue #5 公共部分与目标章节。公共条件标 historical_incomplete，冻结源提交 9e2058fcca7b95389d30e81cb0e52ffe03e2e930；raw_runs unavailable；1MiB 与 8MB 不可混用。目标覆盖 Linux、bytes_per_pair=8000000、packet_bytes=4096、R=1、400Gbps、500ns；问题为 ACK 路线补全如何正式集成及扩大验证，证据 E005-14/E005-15。
- `.venv/bin/python scripts/ara.py show I005-N17`：成功，depends_on 与 primary_dependency 均为 I005-N16；successors=[]；返回迁移事件 EV005-import-20261002。

没有被迫读取整份长纪要；没有读取 issue005.md 全文，也没有读取 N17 前置正文。read 的输出没有相邻 idea 章节，符合 NOTES 描述。

## 本地校验

- `.venv/bin/python scripts/ara.py validate`：退出0，issues=3、ideas=43、dependencies=64、claims=14、observations=2、evidence=37、sessions=3、raw_not_bundled=30。
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v`：退出0，12个测试全部通过。
- `.venv/bin/python scripts/ara.py render --check`：退出0，HTML is current。由于任务禁止写研究记录/程序，采用 PROTOCOL 明确提供的只检查模式，没有执行生成页面的 render。

这些结果证明当前本地解析/结构及页面 freshness 通过，不证明历史仿真复现或 GitHub linked branch 真实性。

## 说明缺口与错误

1. README 的 `issues` 输出只有编号、标题、outcome，看不到 status 或 best/promising。需要按 PROTOCOL 的归属表自行找到 YAML 才能完成重点 idea 查询；建议 README 增加一条直接读取 Issue YAML 的示例，或说明 issues 是简表。
2. README 是新模板叙述（main 只有虚拟根、真实历史将放独立分支），实际当前可读 artifact 已有3个研究 Issue。未查看 Git 状态，因此不判断当前分支或这段说明在 main 上是否正确；对首次读取当前工作目录的人，这段话容易造成预期错位。
3. README 环境示例默认创建 .venv，没有说明已有环境时复用；本次自行复用成功，没有造成阻碍。
4. README 只列 render（写入），只读检查模式 render --check 要继续读 PROTOCOL 才发现。当前任务允许通过该模式完成 freshness 检查。

未发现阻止这些指定查询与本地校验的错误。唯一写入是本报告。

## 二次验收：公开单 Issue 入口与迁移任务记录

2026-10-02，收到更新后重新读取当前 README、AGENTS 与 research-manager skill。README 已明确示例分支、`issue 5`、复用现有 .venv、`render --check`；skill 已列出 `issue N` 的摘要/重点用途。本轮没有直接打开 Issue YAML，也没有读取整份长纪要。

实际命令与结果：

- `.venv/bin/python scripts/ara.py issues`：退出0，新增 #2「迁移集成与记录系统验收」outcome=success；#3/#4/#5 仍为 partial。
- `.venv/bin/python scripts/ara.py issue 5`：退出0，直接得到 status=completed、summary、best_ideas=[I005-N02,I005-N16] 及理由、promising_ideas=[I005-N17] 及理由、open_questions。此前重点查询入口缺口已解决。
- `.venv/bin/python scripts/ara.py issue 2`：退出0，迁移自身 status=completed/outcome=success；best=I002-N02、promising=I002-N01；明确 success 仅表示记录迁移验收，未复跑历史仿真，并保存原raw/环境/二进制未迁入的问题。
- `.venv/bin/python scripts/ara.py ideas --issue 5`：退出0，17个节点。
- `.venv/bin/python scripts/ara.py read I005-N17`：退出0，公共条件及目标正文与首次验收一致；仍只返回公共部分与N17，无相邻章节。
- `.venv/bin/python scripts/ara.py show I005-N17`：退出0，前置/主要前置=I005-N16，后继为空。
- `.venv/bin/python scripts/ara.py validate`：退出0，issues=4、ideas=45、dependencies=66、claims=14、observations=2、evidence=39、sessions=4、raw_not_bundled=29。
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v`：退出0，13项测试通过，含新的 focused_issue_cli。
- `.venv/bin/python scripts/ara.py render --check`：退出1，`ARA error: Generated HTML is stale; run render`。这是本轮当前实际检查结果；没有执行会写页面的 render。

当前查询、按需纪要、环境和本地结构校验均无阻碍。README原有四项使用说明缺口均已补上。唯一未通过的交付检查是生成HTML freshness；需负责集成者更新页面后再检查。本轮唯一写入仍为本报告的追加，不修改程序、研究记录、Git或远端。

## 最终页面 freshness 复查

2026-10-02，收到集成者已完成页面生成的通知后，仅再次运行 `.venv/bin/python scripts/ara.py render --check`：退出0，输出 `HTML is current`。保留二次验收当时 stale 的真实观察；当前最终 freshness 检查已通过，没有剩余阻碍。本次仅追加本段，没有修改其他文件。
