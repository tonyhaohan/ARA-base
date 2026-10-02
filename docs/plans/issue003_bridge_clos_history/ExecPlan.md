# Issue #3 迁移 ExecPlan

## Goal

迁移冻结源Issue #3的11个idea到ARA v1，保留失败、历史原话及证据边界。

## User Raw Prompts

以下逐字复制冻结 `migration/source/issue3-ExecPlan.md` 的 User Raw Prompts，来源：https://github.com/tonyhaohan/mcnf-sim-bridge/issues/3 。本次迁移不把历史话语当作新实验授权。

- "接下来我希望你开一个新的issue以及对应的新分支来做这些事情：
你可能需要在我们之前构造过的clos网络上面把实验调通。我之前应该设计过这个实验：在这个网络里面有 N 个 GPU 和 M 个交换机，每个 GPU 跟每个交换机之间都有 Q 条链路相连。这些链路的带宽都一样，我们可以暂且设置为 400 Gbps。其中每个 GPU 都要向其他 GPU 发送 8 MB 的任务，那么理论上的通信时间就应该是：8 MB × (N-1) ÷ M ÷ Q ÷ 400 Gbps。在不同的 NMQ 之下分别跑这个实验：
1. N 在 2~32 之间取值；
2. N 在 1~16 之间取值；
3. Q 在 1~4 之间取值（不过一般取 1~2）。
你可以参照我给小周写的文档来判断这里面可以修改哪部分，需要修改哪部分，以及不应该修改哪部分。
今晚你的工作目标是：让这个实验在大多数情况之下，都把相对误差压在 8% 以内。但也不可以压成负数，也不能真的压到完全是 0 附近，因为那样肯定就错了。仿真必须在一定程度上能模拟出网络的真实行为，不可以过分简化。结束之后，你写一篇报告文档，告诉我你调了哪些关键的网络行为与参数，给我列一个实验结果表格，横纵坐标分别是 N 和 M，每个格子里面写着理论预期时间、仿真时间以及它们的相对 gap，然后分析这里面每个实验剩下的误差主要来源于哪里？我希望它们主要来源于那些不可被消除的固定开销，以及包切分不均产生的尾部效应。"
- "继续，不必追求每一个整数，只要取值范围内的2的次幂对了就行"
- "你现在已经在我们手动设计的网络路由机制里面达到了目标，现在请你尝试用仿真器提供的仿真网络行为来实现这些功能，并且再次达到目标，尽可能保证我们用的全都是仿真器里提供的经典语义，而不是我们自己造出来的语义。你可以调整里面的参数，但最终要向我汇报你是怎样调整的这些参数。这里面的机制包括你刚才说的：
      - PACKET_PAYLOAD_SIZE=4096
      - RDMA QP 发送
      - host 侧 QP hash 选择 NIC
      - switch 侧 ECMP hash 选择 next-hop
      - Qbb/RDMA 内部按 MTU 发包
      - QP egress queue 内部 round-robin
      - PFC/ECN/QCN/DCQCN/HPCC 参数来自 ns-3 backend config"
- "继续。goal可以稍微放松一点，略略高于8%也不是不行"


## Progress

- 2026-10-02：阅读本仓AGENTS、研究管理skill、PROTOCOL、NOTES；从冻结源迁移11节点、3主张、9证据。历史完整进展不重写，保留在 migration/source/issue3-ExecPlan.md 与 issue3.json。

## Next Steps

- 2026-10-02：由集成执行者汇总依赖、校验、渲染和GitHub实际branch linkage；本分片不创建分支或运行实验。

## Decisions

- 2026-10-02：按源next逆转依赖；多父节点主依赖选冻结图遍历的首个父节点，源未明确primary。
- 2026-10-02：历史accepted科学claim映射supported但显式保留叙述来源限制；未声称本次验证支持。
- 2026-10-02：推荐N03和N11，分别保存机制反例和有直接依据的后续契约方向；Issue3整体partial。

## Evidence and Recovery

- 2026-10-02：冻结源commit 9e2058fcca7b95389d30e81cb0e52ffe03e2e930；文件SHA见 evidence.yaml。记录指向最终集成路径，分片文件位于 .work/migration-parts/issue003/。
- 原始runs、trace、报告和二进制未取得，禁止据叙述记录宣称重跑成功。源Issue原文及全部comments在 migration/source/issue3.json；源历史ExecPlan在 migration/source/issue3-ExecPlan.md，源重建session在 migration/source/ara/trace/sessions/2026-07-12_issue3_reconstruction.yaml。

- 2026-10-02 第二轮：按新增历史迁移契约重新选择主要依赖，理由见audit；主张来源作者未记录，修正provenance为unknown；历史supported仅表示限定历史接口/观测的叙述支持。公共条件标historical_incomplete，差异仅填已知值。
