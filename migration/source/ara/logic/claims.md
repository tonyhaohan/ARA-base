---
status: active
owner: core-maintainers
last_verified: 2026-09-17
scope: mcnf-sim-bridge 项目级 ARA scientific claims
---

# Global Claims

## Issue #3：失败路线与仿真器能力缺口

### C003-01：solverPath metadata 不是 simulator 路由契约

- Statement: bridge bundle 中的 solverPath 只有在 ASTRA适配层把它编译为明确的 QP 和逐跳路由配置后，才能约束真实 packet 路径。
- Status: accepted
- Falsification criteria: 未修改的 raw-rank ASTRA 能直接读取 solverPath 并稳定沿指定完整物理路径发送。
- Proof: E003-03

### C003-02：Lane-expanded proxy 不能替代原始 GPU rank 语义

- Statement: 把每条 lane 展开为独立 ASTRA rank 可以验证容量，但不能证明一个真实 GPU rank 能以同样方式使用多条路径。
- Status: accepted
- Falsification criteria: lane-expanded 与 raw-rank 模型在 rank 数、通信任务和发送资源约束上等价。
- Proof: E003-04

### C003-03：High-K hash 不是可信的 QP 路径配置方案

- Statement: 用几十到数百个 QP 等待 host/switch hash 近似均衡不能表达一个逻辑流允许使用的明确 QP组和完整物理路径。
- Status: accepted
- Falsification criteria: high-K hash 能用少量稳定参数精确、可审计地复现任意指定 QP组和完整路径集合。
- Proof: E003-06, E003-07, E003-08, E003-09

## Issue #6：配置驱动的 QP 与完整物理路径

### C006-01：QP policy 属于 bridge接口层

- Statement: QP、路径组、QP组、逻辑流到 QP组的映射和4KB小包 QP选择应由 bridge接口层生成和验证。
- Status: accepted
- Falsification criteria: ASTRA适配层或 ns-3网络层必须搜索或重新决定这些 policy 才能完成受支持实验。
- Proof: E006-01, E006-04, E006-08
- Dependencies: C003-01, C003-03

### C006-02：完整最短物理路径可以在不替换 RDMA 数据面的情况下固定

- Statement: path-specific destination alias 加逐跳单出口路由能够固定一条完整最短物理路径，同时保留原版 RDMA、ACK、PFC 和拥塞控制行为。
- Status: accepted
- Falsification criteria: native trace 出现配置外的正向 data interface，或必须修改 switch forwarding/hash 才能固定路径。
- Proof: E006-04, E006-09

### C006-03：QP复用必须保存连接级状态

- Statement: 同一 QP 的连续 message 应共享 sequence 和拥塞控制状态；使用相同 source port 重建临时 QP 不等价于 QP复用。
- Status: accepted
- Falsification criteria: 两种实现产生完全相同的 QP 生命周期和 sequence state。
- Proof: E006-05

### C006-04：标准基准默认每条完整物理路径一个 QP 即可

- Statement: 在已测 N/M/Q/R case 中，R=2/4 相对 R=1 没有稳定容量收益，因此 R=1 是最小可信默认值。
- Status: accepted
- Falsification criteria: 扩大网格后出现可重复且显著的 R>1 容量收益。
- Proof: E006-06

## Issue #9：4KB小包 QP选择与可复现编译产物

### C009-01：均匀分配比哈希分配更适合作为默认

- Statement: 在相同 QP组上，均匀分配提供严格的小包数平衡，并在 1MiB 配对实验中比哈希分配更稳定且平均仿真时间更低。
- Status: accepted
- Falsification criteria: 代表性复跑中均匀分配不稳定、出现系统性变慢或比哈希分配更不均衡。
- Proof: E009-02, E009-03, E009-04
- Dependencies: C006-01, C006-04

### C009-02：历史 allocation 语义必须保持

- Statement: 缺少 allocation 字段的旧 benchmark row 必须按生成时的哈希分配解释，不能因默认值变化而重新标注。
- Status: accepted
- Falsification criteria: 找到旧 row 实际由均匀分配生成的证据。
- Proof: E009-04

### C009-03：仿真编译缓存必须绑定 source、binary 和 runtime

- Statement: 可复用 ASTRA 编译产物必须同时验证完整 source SHA、平台、binary 和实际加载的 ns-3/protobuf runtime libraries。
- Status: accepted
- Falsification criteria: 只验证 binary 仍能排除 ABI 混用并提供同等 provenance。
- Proof: E009-06, E009-07, E009-08

### C009-04：已测四个 8 MB/R=1 Linux 场景的均匀分配差距低于 8%

- Statement: 在本轮固定版本、400Gbps、500ns每链路、4096B小包、每有向卡对8,000,000B和四个指定N/M/Q配置下，round_robin的纯带宽理论差距为3.88%～6.39875%，重复运行完成时间一致。
- Status: accepted
- Falsification criteria: 相同配置复跑产生不可解释的不一致，或原始字节/路径/输入配对核验失败；不将该有限结论推广到其他规模或数据量。
- Proof: E006-11, E009-10
- Dependencies: C006-02, C009-02

### C009-05：本批11个扩规模配置重复稳定，但8%不是已验证的全局上界

- Statement: 固定版本、8MB有向卡对、400Gbps/500ns链路、4096B小包、R=1均匀分配下，本批11个指定8/16/32卡配置通过实际输入和原始结果验收，两遍完成时间相同。10个gap低于8%，8/2/4为8.36714%；32/2/2每遍有156条PFC暂停和156条恢复记录。
- Status: accepted
- Falsification criteria: 相同固定配置不能复跑，或输入、FCT、路径核验失败；不把此有限结论推广到未测规模、多阶段Allreduce或真机。
- Proof: E009-11, E009-12
- Dependencies: C006-02, C009-03

### C009-06：已测原版高Q场景存在ACK回程平行接口遗漏

- Statement: 固定Linux构建的8/2/4和8/4/2全量性能trace显示ACK仅经过每对相邻节点最后平行链路；实际common.h以节点对为键覆盖接口。正向显式别名路径不受相同遗漏影响，导致ACK集中而正向数据可使用全部链路。
- Status: accepted
- Falsification criteria: 匹配版本/配置的完整trace或实际普通路由表显示ACK已均匀覆盖全部平行接口，或源码证据与所用二进制不匹配。
- Proof: E009-14
- Dependencies: C006-02, C009-03

### C009-07：隔离ACK回程补全候选在四个指定配置中有效且保留数据语义

- Statement: 保留QP、正向路由、ET、字节、400Gbps/500ns和原ACK/PFC，只补遗漏普通目的IP路由后，8/2/4和8/4/2差距从8.36714%/6.325%降至5.20857%/5.00429%，32/2/2从4.28194%降至3.29016%，Q1对照不变；各两遍相同。候选尚未替换默认实现。
- Status: accepted
- Falsification criteria: 同配置复跑不一致、独立守恒/输入检查失败，或实际改善需减数据、关协议、改带宽。此结论不承诺全网格收益或跨版本通用修复。
- Proof: E009-15
- Dependencies: C009-06

## Issue #11：项目级 ARA 架构

### C011-01：一个研究项目只维护一张全局 DAG

- Statement: `mcnf-sim-bridge` 的所有研究 Issue 必须写入同一个 `ara/trace/exploration_tree.yaml`；Issue view 不能成为第二事实源。
- Status: accepted
- Falsification criteria: 原 ARA 协议要求同一研究项目按工作项拆分多个 exploration graph，或全局图无法表达 Issue #6 到 #9 的因果关系。
- Proof: E011-01, E011-02, E011-03

### C014-01：受限回程补全可以在正式 bridge 入口保持对照与可验证性

- Statement: 在本次已核验实际构建、完整无故障单层 Clos 的 25 个配对场景中，显式回程补全复现候选收益，legacy/Q1/正向数据保持，缓存与构建身份保护通过测试。该结论不保证任意数据量低于 8%。
- Status: accepted
- Falsification criteria: 同一已声明范围不能复现、输入/字节/完成核验失败、未知构建被误放行，或两策略缓存与结果混用。其他构建/拓扑及硬件不在当前支持范围。
- Proof: E014-01, E014-02, E014-03, E014-04, E014-05, E014-06, E014-08
- Review refinement: 首版存在 legacy-only 保留 complete 成功行的增量核验缺口，后由 E014-08 的反例及真实混合入口回归修复；不改原性能数表。按 E014-07，8% 非验收线；E014-09/10 不把尾部算术或 RDMA 参考推广为 NVLink 硬件证明。
- Dependencies: C009-07

### C016-01：四卡双层合成通信保留共享瓶颈且真实运行可重复

- Statement: 固定四卡、两下层、一或两上层、相邻单链路400Gbps每方向/500ns、4096B/R1原生ACK下，同组/跨组P2P和单/双上层全互传通过输入、FCT与全trace逐跳验证；四种8MB性能各两遍一致，载荷下限160/160/640/480us，差距2.621875%～3.976875%。
- Status: accepted
- Falsification criteria: 同一冻结源码/输入无法复现，或独立原始路径/字节/完成核验失败。只适用四个指定合成案例，不推广至未测规模、多阶段Allreduce、坏卡或NVLink真机。
- Proof: E016-02, E016-03
- Dependencies: C009-03

### C017-01：有限扩规模保持数据与重复性，但四上层16卡存在真实动态尾部

- Statement: 固定8个双层CLOS合成配置全部真实完成且精确重复；五点差距2.56%～3.42%，16卡4上层4/8/16MB为33%～35%。高差距由同组传输拖住最终完成，8MB的GPU接入发送有约985us内部空闲，不能由至多0.1728%的静态分片下限增量解释。
- Status: accepted
- Falsification criteria: 冻结输入/构建无法复现，或原始路径、数据、FCT分组、逐口序列化核验失败。共享priority暂停与per-QP调度是有源码依据的机制，但尚未隔离各机制的因果延迟；不推广至Allreduce或NVLink真机。
- Proof: E017-02, E017-03, E017-04
- Dependencies: C016-01

### C017-02：四上层的GPU接入空闲主要与共享暂停重合，不能等同于可消除的因果延迟

- Statement: 固定16卡四上层8MB完整trace逐段对齐显示，每GPU95.32%～95.94%的发送口空闲发生在priority3暂停期间；同优先级组内/跨组数据与ACK共享暂停。跨组源包全部发完时，每GPU仍有41.725440～41.979392MB组内数据未发，形成后续尾部。相同计算在S1/S2对照没有组内剩余。当前CC12源码未启用反馈降速，不能以VAR_WIN等标志推断发生动态变窗。
- Status: accepted
- Falsification criteria: 冻结trace、实际代码或独立区间核算不支持暂停语义、交集及剩余字节；不把观察重合推广为关闭PFC的净收益，不将始终同等eligible的QP轮询假设当作已证事实。
- Proof: E017-05
- Dependencies: C017-01
- Follow-up: E017-06进一步重建S1/S2/S4窗口状态。S4跨组512QP均无窗口受限待发时间，S2跨组QP时间有91.3126%窗口受限，支持两者可发送集合不同；比例不是任务延迟，也不构成关闭流控的收益证明。

### C017-03：真实机制依据不能替代当前简化模型的硬件标定

- Statement: 一手PFC文档支持同优先级多流共同暂停，mlx5手册支持默认公平与显式QP分组配置；但没有由这些资料建立当前181c785逐包QP轮询、固定窗口和显式pause/resume时序对指定硬件的精确等价。NVLink资料也不能把RDMA QP/ACK/PFC直接重命名为NVLink机制。34.68%仍是容量下限差距，而非已测硬件误差。
- Status: accepted
- Falsification criteria: 引用原文或冻结源码与所述机制矛盾，或已有指定硬件、配置与工作负载的对照数据建立本文尚未确立的等价。文献中的公平意图不作为逐包算法保证；未来新增硬件证据可缩小限制。
- Proof: E017-07
- Dependencies: C017-02

### C018-01：该双层单点对QP布局高度敏感，但更短时间不证明更真实

- Statement: N16/S4/每有向卡对8MB固定网络对照中，将同组每卡对1QP改4QP，跨组及实际数据链路载荷不变，完成时间3447.875→2634.101us（相对2560us容量下限差34.682617%→2.894570%）；首遍/重复一致且旧baseline精确复现。GPU0忙时保持2460.960us、暂停重合空闲943.354→85.712us。证据支持当前模型对QP布局敏感，不能单独归因公平性或据此选择真实硬件模型。
- Status: accepted
- Falsification criteria: 冻结输入/构建不能复现，跨组原QP五元组、路径或业务字节未保持，原始FCT/trace核验失败；或同组聚合窗口变化被错误忽略。仅覆盖一个合成All-to-all点，原默认保留。
- Proof: E018-01, E018-02, E018-03
- Dependencies: C017-03

### C019-01：多QP的16卡收益跨三个数据量复现，但并非单调性能定律

- Statement: 固定四上层双层CLOS、同组1QP对4QP且跨组不变时，N16的4/8/16MB完成时间减少22.63931%/23.60219%/24.15125%，而N8/8MB慢1.171us（约0.10163%）。24次真实运行的输入、FCT、路径与字节核验通过；每套性能重复一致。16卡忙时不变且暂停重合空闲明显缩短，8卡无暂停或窗口阻塞且忙时不变。结论是有限范围QP布局敏感性，不是QP越多越好。
- Status: accepted
- Falsification criteria: 冻结输入/构建不能复现，原始FCT或数据路径/字节审计失败，或两配置业务载荷/物理带宽/跨组布局实际改变。复现不要求原始trace逐字节相同；不能将QP数与聚合窗口共同变化解释成纯公平性收益，或将容量下限差距解释成硬件误差。
- Proof: E019-01, E019-02, E019-03
- Dependencies: C018-01

### C020-01：固定四上层32卡的QP布局收益可复现，但暂停次数并非收益指标

- Statement: 在固定两下层四上层、32卡1/4MB有向全互传中，同组1→4QP且跨组布局不变时，完成时间1464.489→1318.466us、6093.800→5264.348us，减少9.97092%/13.61141%。原配置同组迟发尾部缩短，忙时不变且暂停重合空闲下降，但pause事件数反而增加。18次有限矩阵包含旧16卡对照，数据/路径/FCT/重复均核验通过；不推广为QP越多越好。
- Status: accepted
- Falsification criteria: 冻结输入/构建无法复现，原始FCT、字节、物理路径/载荷或暂停窗口区间重建失败；或同时变化的聚合窗口被错误归为纯调度收益。容量下限差距不是实测硬件误差，默认保持，不声称所有双层拓扑或求解器Allreduce已验证。
- Proof: E020-01, E020-02, E020-03
- Dependencies: C019-01

## Open Questions


### Q001：Linux 论文级归档

- Question: 在干净 Linux 环境重建并复跑代表性 QP 与 allocation case 后，当前结论和理论gap是否保持？
- Status: open
- Related nodes: I006-N10, I009-N10
- Progress: 2026-09-15 完成四个R=1、8MB拓扑的hash/round_robin配对与复跑，见 I006-N13、I009-N11；尚未覆盖R=2/4、全网格或解释历史跨构建微差，故本问题仍保持open。
- Progress: 2026-09-16新增11个R=1均匀分配扩规模配置，见I009-N12/N13；最大32卡。全网格、R=2/4归档及新观察的具体因果仍未完成。
- Progress: 后续受控诊断与候选见I009-N14至N17；已定位ACK回程遗漏，近期失败已恢复，尚未完成正式集成/广泛回归及PFC单独贡献分解。
- Progress: Issue14 已完成限定实现与 100 次配对性能回归，包括代表性 R2/R4 与 4/16MB；见 I014-N03/N04。4MB 存在超 8% 残差；全网格、跨构建与 PFC 单独贡献仍未完成，保持 open。
