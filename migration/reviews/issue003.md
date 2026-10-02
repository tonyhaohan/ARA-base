# Issue3 migration audit

产物：11 ideas / 3 claims / 9 evidence / 0 observations / 1 import event。源staging没有I003相关观察，未从历史结论倒造观察或过去crystallize事件。

可独立按协议完成迁移。自行判断处：源next逆转后有多个父节点，但源无primary，采用冻结图首个父节点；旧claim accepted映射supported并加历史叙述条件；源Issue总结未规定收尾outcome，从部分达标与未解决small-N判partial。推荐由负结果有用性与明确后续方向选择N03、N11。现协议没有定义迁移accepted→supported规则，建议明确这是历史状态转换而非证据升级。

证据location允许指向本地叙述文件，但协议对raw_availability区分需读完整说明：此分片标unavailable表示原trace/运行产物不可取得，location中的ExecPlan本身已bundled。未取到原报告、runs、trace和历史二进制；不能复验数字。E003-09地点选源Issue6 ExecPlan，I003-N11的跨Issue evidence E004-01/E004-08保留，由另一分片提供。

本分片没有实际绑定GitHub分支、运行全仓validate/render或仿真；必须由集成阶段完成结构验证。历史源plan引用旧工具和路径，不要求在本仓可执行。Markdown overrides={}只是未重建结构化覆盖，正文保留全部差异；协议未规定历史迁移缺条件时的最小覆盖表达。

## 第二轮：新增历史迁移契约复核

已读docs/PROTOCOL.md历史迁移契约。公共条件明确conditions_status: historical_incomplete及缺失原因，7个idea填已知覆盖，其余空覆盖不表示没有差异。

主要依赖变更（当前迁移者解释，非源作者指定）：
- I003-N03 → I003-N02：解析估计不能证明路由，继而用raw-rank探针检查真实注入。
- I003-N06 → I003-N04：lane代理改变GPU rank语义，直接促成保留原rank并验证原生RDMA机制的问题。
- I003-N08 → I003-N07：native all-to-all未得到M/Q伸缩，促成增加独立QP的hash近似。
- I003-N09 → I003-N08：high-K striping仍不能覆盖Q平行链路，促成让链路成为可见next-hop。
- I003-N10 → I003-N09：QP hash与ECMP-visible拓扑仍有小N残差及路径契约缺口，促成最后参数搜索。

三项claim维持限定历史supported：C003-01由raw-rank反例与接口语义支持，C003-02由rank数与资源约束变化支持，C003-03由hash没有指定QP组/完整路径契约的接口限制支持；均不是凭用户转向证明性能。源未记载claim作者，provenance改unknown；原statement逐字保留并缩限conditions。

直接调用scripts/notes.py parse_document/detail_fields：11/11 idea必要字段非空，覆盖question/decision/experiment/dead_end/pivot五类型；9/9本地证据SHA256仍匹配。未运行全局render。新增规范已解决首轮机械primary、claim映射、空覆盖和可获取性的歧义。
