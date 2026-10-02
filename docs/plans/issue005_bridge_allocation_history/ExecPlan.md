# Issue #5 历史迁移 ExecPlan

## Goal

将冻结源 Issue #9 的17个I009原生节点迁移v1，保留失败、限制与历史事实；不重新运行实验。

## User Raw Prompts

### 源Issue正文（逐字）

出处：https://github.com/tonyhaohan/mcnf-sim-bridge/issues/9；本地冻结副本 migration/source/issue9.json。

在现有 N/M/Q/R Clos QP 基准中，为每个逻辑流使用 1MiB 数据，对比 hash 与 round-robin 两种4KB小包 QP选择方式。记录完成时间、理论差距、QP负载离散程度和运行稳定性。若 round-robin 稳定且结果符合预期，则将正式性能仿真的默认策略改为均匀分配，同时保留 hash 作为可选配置和对照能力。

不修改 ASTRA 或 ns-3 源码；优先复用 bridge 已有的 messageAllocation 配置。

updated at 2026/07/11 23:21
written by codex local

### 源allocation ExecPlan原文

出处：migration/source/issue9-plan/ExecPlan.md；源 https://github.com/tonyhaohan/mcnf-sim-bridge/issues/9 。

- “测试一下均匀分配和hash在1MB任务下gap能差多少？均匀分配肯定更均匀一些，如果这个功能稳定的话我们就把这个设为默认吧。”
- “好的，继续吧。另外我希望这样管理我们的编译产物：每次根据我们Astra代码库的某个sha值（类似于git commit号的前七位？）追加到编译产物名称后面，然后每次跑之前确认一下是否匹配的上，匹配不上就重新编译，能匹配则复用，你觉得可以吗？”
- “很好，把这部分内容提PR，然后我们继续对齐词汇。我感觉差不多了？还有要对齐的吗”


### 源诊断ExecPlan原文

出处：migration/source/ara/evidence/archive/issue9_clos_gap_diagnosis/ExecPlan.md；源Issue #9历史研究后续要求。


“我觉得不急着往后推，先把现在的工作做扎实，一方面，差距较大的实验找找原因，看看能否优化？另一方面，失败的实验，找找原因，能否成功跑出来？”


## Progress

- 2026-10-02T13:56:15+08:00 迁移事实：17 ideas、15 evidence、7 claims、1 observation；SHA256本次核验。历史实验数字来自冻结报告，未本次重跑。

## Next Steps

- 2026-10-02T13:56:15+08:00 主agent集成分片后执行全局validate/test/render及在线分支验证；本执行者未更改Git或远端。

## Decisions

- 2026-10-02T13:56:15+08:00 将来源next反推前置并合并also_depends_on；primary取首个反推next前置，否则首个also依赖。源无显式primary，这一选择是迁移判断，不是历史事实。
- 2026-10-02T13:56:15+08:00 原claim accepted转历史supported，证据仍标原始数据未取得；迁移不提升经验支持。

## Evidence and Recovery

- 冻结源提交：9e2058fcca7b95389d30e81cb0e52ffe03e2e930；mapping：migration/mapping.json。
- 完整源执行历史见 migration/source/issue9-plan/ExecPlan.md 与 migration/source/ara/evidence/archive/issue9_clos_gap_diagnosis/ExecPlan.md；未重写其原始历史。
- 恢复入口：ara/issues/issue005.md；证据索引由迁移分片evidence.yaml集成。

### 第二轮迁移复核 2026-10-02T14:03:18+08:00

按新增历史迁移契约补正文固定字段与不完整条件标识，逐项调整科学状态与主要依赖；所有变更为迁移解释而非新实验事实。17章节五种类型的必需字段经现有detail_fields检查通过。原用户原文未改。
