# Issue004迁移审计

产物：15 ideas、13 evidence、4 claims、1 observation、1当前import session。保留三个设计/流程负结果、归档覆盖失败和包装字段失败以及近似复现局限。

文档可用性缺口：
- PROTOCOL说明主要依赖恰好一个，但旧源只有next/also_depends_on，未规定如何挑选；本次以反向next列表首项为主要依赖，其余保留。
- claims旧accepted到v1证据状态无迁移规则；规范性C004-01、语义C004-03保守标hypothesis，测量C004-02/04为有限范围supported；源原文保存在冻结claims.md。
- evidence本地报告存在而raw不存在时的raw_availability需要自行判断；以unavailable明确缺失，并存储实际报告SHA。
- NOTES仍称虚构样例且引用旧extract_idea.py，与实际PROTOCOL不完全一致；采用其中Markdown层级和metadata规则。
- 当前工具正在主agent实现；未调用可能写全局的render。分片独立YAML解析与文件SHA检查完成，全局DAG/跨Issue引用需集成后校验。
- Issue依赖独立归纳为[3]：3是原设计起因；5是后期allocation/cache复现所引用成果，保留于细粒度边而不投影为Issue层前置，避免4与5交错工作形成Issue环。

未获取：源runs/issue6_qp_binding_key_cases、clos_qp_benchmark_coarse，外层outputs/clos_reproduction_20260915、clos_scaling_20260916、clos_diagnosis_20260916（包括failure_recovery.md），真实二进制与完整原始trace/FCT。历史证据索引及报告虽已归档，不能等同本次实验复现。

## 第二轮：新增历史迁移契约复核

- 重新阅读PROTOCOL历史迁移契约与更新NOTES，原第一轮缺口记载保留；当前主要依赖、状态映射、条件不完整、报告与raw边界已有明确规范。
- 公共条件标conditions_status: historical_incomplete并说明缺少全部环境/输入/历史构建身份；移除非真实条件差异config.experiment_scope。各idea overrides={}仅表示未单独归档确切差异，不表示历史条件完全相同；正文保留已知method/result。
- 主要依赖重新判断：I004-N03改为I004-N02，因失败的high-K契约直接促成bridge显式policy；I004-N15改为I004-N11，因首个校准归档失败是双失败恢复审计的主要触发之一，I004-N14和I005-N14仍保留细粒度前置。I004-N10保留I004-N06，因persistent连接语义是最终采纳接口的关键能力，ownership修正及R=1决定作为共同前置；其他单父选择直接沿源来由。I004-N11保留I004-N10，采纳的配置驱动接口是运行对象，I005-N10是后期allocation/cache复现条件。
- C004-01/03仍hypothesis：规范或语义断言不能仅因采纳或单个reuse smoke升级为普遍科学证明；C004-02仅trace支持已测四条完整路径的有限机制、C004-04仅12例代表粗扫支持R=1的有限选择，保留supported及范围。来源作者未记载继续unknown。
- 修正reproduction为{notes: ...}映射，符合当前validator的复现入口字段结构。
- scripts/notes.py parse_document/detail_fields逐节点验证15个idea全部类型必需正文及partial/rejected/superseded lesson均非空；13报告SHA重新核对通过。未运行全局render或修改全局文件。
