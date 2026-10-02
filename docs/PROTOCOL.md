# ARA Base v1 数据契约

这是 ARA 的项目适配协议。所有路径相对项目根，`ara/` 是唯一活动 artifact。两层依赖分别校验，不从 idea 边自动投影 Issue 边。

## 文件与事实归属

| 文件 | 唯一维护的内容 |
|---|---|
| `ara/project.yaml` | schema_version=1、title、GitHub `owner/repo`、root=I000-N00 |
| `ara/trace/ideas.yaml` | idea 身份、类型、当前状态、来源、前置依赖和纪要定位 |
| `ara/issues/issueNNN.yaml` | Issue/branch 绑定、独立 Issue 依赖、总结、两组重点 idea |
| 同名 `.md` | 公共条件与各 idea 详细记录 |
| `ara/logic/claims.yaml` | 科学主张的当前版本及证据状态 |
| `ara/staging/observations.yaml` | 原始观察，保留至今；其转换过程由事件记录 |
| `ara/trace/sessions/*.yaml` | 按时间追加的捕获、转换、修订和冲突事件 |
| `ara/evidence/index.yaml` | 证据位置、身份、复现入口、小结果及可获取性 |

## Idea DAG

```yaml
ideas:
  - id: I000-N00
    type: root
    title: 研究起点
    depends_on: []
  - id: I003-N01
    issue: 3
    type: question
    title: 能否验证这个假设？
    status: open
    provenance: user
    timestamp: '2026-10-02T14:00:00+08:00'
    depends_on: [I000-N00]
    primary_dependency: I000-N00
    record: ara/issues/issue003.md
    evidence: []
    evidence_note: 问题尚未实验。
```

真实节点类型为 question、decision、experiment、dead_end、pivot；状态为 open、accepted、partial、rejected、superseded。这里 accepted 表示记录中已采纳的结果/决定，不替代 claim 的科学证据状态。provenance 为 user、ai-suggested、ai-executed、user-revised。

节点只写 `depends_on`，其中恰好一个是 `primary_dependency`。不允许 next、children、also_depends_on。根没有 Issue、主要依赖、证据或纪要；没有真实前置知识时依赖根，有真实依赖则不能混入根。根可有任意多个后继；全部后继在读取时反推。ID 不重用，数字位数不限，同数值不同补零方式不能成为两个 ID。

纪要的结构化正文使用围栏外 `### question` 等固定字段标题。question 需要 question；decision 需要 choice、alternatives；experiment 需要 hypothesis、method、result；dead_end 需要 hypothesis、result、failure_mode、lesson；pivot 需要 trigger、new_direction、result。字段值保留自然语言，内部代码使用围栏，追加运行用四级标题；不在图中重复这些正文。

accepted 的 decision/experiment/pivot 必须有 evidence；其他空 evidence 必须有 evidence_note。dead_end 必须在纪要里记录失败原因和经验；partial/rejected/superseded 也必须保留限制或经验。节点可能跨 Issue 依赖，节点文件顺序不表示依赖顺序。

## Issue 总结

```yaml
issue: 3
title: 验证某个假设
url: https://github.com/owner/repo/issues/3
branch: codex/issue3-topic
status: completed
outcome: partial
depends_on: [2]
summary: 已获得限定范围内的结果，仍有开放问题。
record: ara/issues/issue003.md
execplan: docs/plans/issue003_topic/ExecPlan.md
best_ideas:
  - id: I003-N02
    reason: 在本轮已测方案中效果最好，仍受记录中的条件限制。
promising_ideas:
  - id: I003-N03
    reason: 已定位失败机制，有明确可验证的后续方向。
open_questions: []
```

status 为 active/completed；outcome 为 open/success/partial/failed。分支名包含对应 Issue 编号，实际通过 `gh issue develop` 绑定，在线校验要求只关联一个分支。分支名不能给其他 Issue 重用；main 是集成分支，不作为研究分支。

两组重点 idea 均非空，允许多个和重叠，必须是本 Issue 的真实节点；每个入选都有 reason。失败 Issue 仍然选相对有用的尝试和可继续追查的方向，不伪造成功。Issue 依赖是收尾时有理由的概括，可忽略细粒度跨 Issue 边，不能删改细粒度证据来迎合概览。

## Claim 与观察

Claim 必需字段：id、statement、conditions、status、provenance、falsification、evidence。status 为 hypothesis/untested/testing/supported/weakened/refuted/withdrawn；supported 或 refuted 必须有证据。observations、depends_on（其他 claim）可选。仅由用户同意、agent 推测或话题结束不能证明一个科学主张成立。

Observation 必需字段：id、issue、timestamp、provenance、text、context、bound_to、promotion_condition。bound_to 引用真实 idea；观察不可因形成结论而删除。是否已形成结论、形成什么、何时形成，由 session 事件计算。

新旧知识有冲突时保留双方，记录 conflict 事件，后续用 resolve 事件及理由收束。开放问题可以继续存在，不要求为了完成记录而强行作结论。

## Session 与转换

```yaml
id: S003-20261002
timestamp: '2026-10-02T14:00:00+08:00'
issues: [3]
summary: 配对实验完成，限定范围内形成主张。
events:
  - id: EV003-01
    action: crystallize
    timestamp: '2026-10-02T14:00:00+08:00'
    provenance: ai-executed
    from: [O003-01]
    to: [C003-01]
    trigger: empirical_resolution
    evidence: [E003-01]
    rationale: 相同条件的配对结果支持该主张的限定范围。
```

action 为 capture/crystallize/revise/conflict/resolve/withdraw/import。每条事件有全局唯一 id、timestamp、provenance、rationale。from/to/refs 引用已存在条目；crystallize 必须从 observation 指向 claim 或真实 idea，记录 trigger（user_affirmation/empirical_resolution/artifact_commitment/topic_abandonment）。正式化不等于 supported。

revise 必須有 subject、before、after，完整保留被改条目的前后内容；resolve 必须引用待解决的 conflict 事件。历史迁移使用当前时间的 import 事件，保留原始材料，不编造源记录未保存的过去转换过程。迁移时来源不明可明确记录 unknown，不能把它升级为已核实的来源。

## 证据

每条 evidence 需要 id、kind、summary、location、identity、reproduction、result、raw_availability。location 是项目内相对路径或 https 地址；identity 包含已知 commit 和/或 sha256，本地文件的 sha256 必须真实匹配。reproduction 记录命令、配置、环境或说明这些信息为什么没有保存；result 提供小结果或明确非数值证据。

raw_availability 为 bundled/external/unavailable/not_applicable。一个本地报告可完整归档，而它引用的原始 trace 尚未随仓库保存：此时标 external/unavailable 并保留 limitations。validator 验证本地内容与指针格式，不主动下载远程证据，不把结构通过说成仿真复现通过。

## 变更与校验

`validate` 检查两层 DAG、根、字段、双向可解析引用、重点列表、纪要、事件和本地证据身份。`validate --github` 额外检查仓库、Issue 与唯一真实 linked branch。`render --check` 检查页面 freshness。

`history --base COMMIT` 对比 Git 历史：已存在 idea 不得删除；观察内容不可改写；session 事件只能追加；公共条件和既有 idea 纪要只能追加；ExecPlan 除 Goal 外按章节追加，原始用户话语不可删改。claim 当前版本或 idea 当前状态的改动必须有新的 revise 事件，携带实际 before/after。这是对可见 Git 基线的检查，不能证明基线之前记录了所有研究活动。

## ExecPlan

每个研究 Issue 一份 `docs/plans/issueNNN_topic/ExecPlan.md`。使用 `## Goal`、`## User Raw Prompts`、`## Progress`、`## Next Steps`、`## Decisions`、`## Evidence and Recovery`。Goal 可修改；其他章节的原有内容保留并追加，更新时注明时间和被取代的决定。原始用户要求逐字记录，来源为外部 Issue 时保存原文及链接。ExecPlan 服务于执行恢复，纪要服务于知识读取，二者只相互引用。

## 历史迁移契约

- 在冻结版本读取全部节点，反转所有 `next` 并合并 `also_depends_on`，去重后写 `depends_on`。检查所选集合前置闭合；未迁移前置不能悄悄删除。
- 原版没有主要依赖时，由迁移者选出最能解释当前idea来由的一个；这是新的索引判断，记录选择依据，不能宣称源作者指定过。机械首父选择只作为缺乏更明确信息时的可追溯默认。
- 新ID和源ID通过迁移映射保存；活动纪要不再复制旧next等边字段，完整旧数据原样归档。
- `accepted` 是旧记录状态。idea状态保留；claim科学状态逐项判断。只有来源证据支持的限定主张可以标历史supported；流程要求、未测断言保持hypothesis/untested，来源作者未记载时用unknown。迁移不升级证据强度。
- 历史公共条件不完整时显式写 `conditions_status: historical_incomplete` 和原因。此时overrides仅列已知差异，空映射不能推断历史完全没有差异；方法正文和冻结来源保留实际已知条件。新研究应填写完整公共基线和确切差异。
- 本地证据location可能指向已归档报告，而raw_availability=unavailable说明该报告所依据的原始运行未取得，两者不矛盾。
- 迁移产物的summary/primary/highlights和状态判断属于当前agent的迁移解释；原始事实保留原时间与出处，当前转换使用import事件。不逆向捏造从未记录的observation或crystallize事件。
