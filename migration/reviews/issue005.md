# Issue005迁移审计

产物：17 ideas、15 evidence、7 claims、1 observation、1当前时间import事件。未获取原始runs/、trace、服务器源码快照、binary/runtime库或在线PR审阅；只有冻结报告可本次SHA核验。失败N07/N09保留；近期外层失败的恢复见源诊断报告，外Issue恢复节点仍通过依赖保留。

文档可用性缺口及自行判断：
- 源格式next/also_depends_on与v1 depends_on转换规则未规定；反推全部incoming next并合并also，primary优先首个主链incoming，保留原字段在纪要。
- 源claim accepted不属于v1科学状态；阅读已有实验/审阅报告后选历史supported，明确未重新复现；来源作者未保存，provenance使用unknown。
- 源observation没有context/bound_to；context引用原resolution，bound_to根据原文显式节点设置。
- 文档没定义迁移分片布局、列表键整合规则；按协议使用ideas/claims/evidence/observations，session顶层结构。
- Issue状态：历史已有closeout而后续问题仍开放，因此completed/partial只表示历史记录交付；在线Issue/唯一分支由主agent另验。
- docs/NOTES.md仍声称虚构样例并提供旧extract命令，和本仓真实迁移/ara.py路径不一致；未把虚构环境引入历史。

验证：17节点集合匹配原I009，节点状态和类型保存；所有本地证据SHA重新计算。全局validator需其他Issue分片及主agent工具完成后运行，分片不能独立证明全图引用闭合或Github绑定。

## 第二轮审阅 2026-10-02T14:03:18+08:00

已按新增历史迁移契约重写活动纪要固定字段，去除next/also_depends_on副本，完整源图仍在migration/source。公共条件标historical_incomplete及原因，各idea只写已知overrides。实际scripts/notes.py parse_document/detail_fields读取17章节及全部5类必需字段通过。逐项审阅claim：C005-02旧行语义与C005-03缓存必须约束为untested；其他5条限定历史经验主张supported并补明范围，迁移未重跑。primary调整N05→N04、N09→N08、N12→I004-N13；原所有前置保留，选择理由与完整before/after revise事件记录。第一轮文档缺口现已补规范，前段审计作为历史保留。未运行全局render。

## 第三轮字段类型修复 2026-10-02T14:08:16

对照当前scripts/ara.py证据校验，将15条reproduction字符串无损包入{explanation: 原字符串}映射；逐条核验原文本完全一致。全部15条的reproduction/identity映射、必需字段、ID、raw_availability和本地SHA256再次通过。仅更新本分片evidence.yaml与此审计记录，没有修改集成文件。
