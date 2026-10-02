---
status: complete
owner: codex-local
last_verified: 2026-09-16
scope: 单层Clos残余差距诊断、受控优化与近期失败恢复核验
---

# 先查清单层 Clos 的差距与失败


按docs/guideline/PLAN.md维护。本任务接续Issue #6/#9研究，不提交或推送，不创建外部Issue/PR，不修改仿真器核心，不覆盖已完成实验。

## Purpose / Big Picture


暂停真实求解器接入、双层Clos和UBMesh。解释8/2/4相对纯带宽理论的8.36714%差距，并判断能否在保持完整路径、数据量和协议真实性的前提下改善。复核近期两个失败批是否已被修正后的同配置运行覆盖。成功意味着原因和证据对应、失败不被掩盖、优化前后可比较，而非强求所有差距小于8%。

## User Raw Prompts


“我觉得不急着往后推，先把现在的工作做扎实，一方面，差距较大的实验找找原因，看看能否优化？另一方面，失败的实验，找找原因，能否成功跑出来？”

## Progress


- [x] 2026-09-16：重读规范、ARA全局图、当前结果；已知8/2/4与8/4/2同为140us理论时间而仿真差2.859us。
- [x] 2026-09-16 11:24 CST：检查服务器约29GiB可用内存、88GiB磁盘，无现有仿真运行。root读Git被所有权保护拒绝，后续以源码所属mcnfsim用户检查，不放宽安全设置。
- [x] 两个近期失败恢复核验完成：归档覆盖问题按策略/遍数隔离后16次重跑成功；字段错误修正后12次成功。80+5个关键输入/FCT文件逐字节相同，原失败保持原样。
- [x] 两个8MB基线trace开关结果精确相同，独立验收8个诊断案例10752条FCT、每例8卡完成；全量trace各1203664记录、448000000字节、109424个唯一包，路径/序号守恒。
- [x] 4/8/16MB对照完成；时间差随数据量扩大，不能只归因固定启动开销。全量trace确认ACK集中到每组最后平行链路，最忙链路序列化149643/146773ns，相差2870ns近于实测2859ns。
- [x] 在新qp_config中补齐普通目的IP的缺失回程接口，不改核心：8/2/4为147.292us，8/4/2为147.006us；8/2/1不变579.554us；32/2/2为1280.798us。四配置各两遍相同，32卡PFC由312条变为0。候选独立验收PASS：21472条FCT、224个ET文件，两个目标全量trace守恒与ACK覆盖通过。
- [x] 归档分析、ARA、命令与未解决项完成；全局结构校验44节点/65边/40证据/15结论/7会话通过，19项记录测试通过，git diff --check无错误。两名独立审阅者未发现阻断问题。

## Context and Orientation


bridge本地为D:/codex/集合通信仿真26暑/mcnf-sim-bridge，已有记录分支codex/6-linux-clos-reproduction；服务器源码在/home/mcnfsim/mcnf-smoke/mcnf-sim-bridge，固定1d4f816，ASTRA固定181c785，ELF SHA256为7f9db19d50dafbe8d371c9f64cbef8b9e7b27cb7794fb1c62e6be8956ade67f4。运行用户mcnfsim；解释器为同父目录server-smoke-kit/.venv-linux/bin/python；protobuf路径/usr/lib/x86_64-linux-gnu。

N/M/Q/R分别为卡数、并行交换机数、每卡每交换机平行链路数和每完整物理路径QP数。本次R=1、4096字节小包、400Gbps/500ns链路、均匀分配，8MB每有向卡对，理论时间160*(N-1)/(M*Q)us。QP是绑定固定完整路径的逻辑发送通道，不能把Q说成QP数。

原结果为outputs/clos_scaling_20260916/clos_scaling_20260916_extended_ftlIDF，其中8/2/4=151.714us，8/4/2=148.855us。32/2/2在core_8QrZpA中出现156暂停及156恢复，不能用它解释没有PFC的8/2/4。正式输入可在各first/round_robin/cases目录找到。两个近期失败为clos_reproduction_20260915_dXbRHT与clos_scaling_20260916_core_86J6hV，原始证据保持原样。

## Plan of Work / Milestones


第一阶段并行只读审查失败与代码。第二阶段只在新实验目录复制或等价再生成输入，重跑两个8MB基线并开启全量trace；用实际输出证明trace开关没有影响时间。解析每条有向物理链路的数据、协议头、确认包和发送空闲区间；不把跨链路的等待时间简单相加。必要时用4MB与16MB控制实验检验大小敏感性，不把较大数据量本身当作优化。

第三阶段依据观测选择最小干预。早期候选为错开QP余包分配，但两场景正向负载相同而ACK回程缺失平行出口的证据更强，因此未实施余包策略。实际候选仅向qp_config追加普通GPU目的IP遗漏的前Q−1个平行接口，保留默认已安装的最后接口。使用原版hash选路、ACK生成、PFC、包大小、带宽与传播时延；正向alias路由、QP、消息与ET不变。它是隔离输入候选，不冒充师兄原版，不替换仓库默认值。

## Concrete Steps


本地新工具和拉回产物均放outputs/clos_diagnosis_20260916。服务器以mktemp新建experiments/clos_diagnosis_20260916_XXXXXX，用tmux运行；日志、时间、输入指纹和失败保留。只同步新增包装/分析脚本，既有源码不变。每命令限600秒、CPU0-7、虚拟内存12GiB，启动前可用内存至少8GiB。

## Validation and Acceptance


数据与FCT逐条核对，总字节为N*(N-1)*S；实际qp_config、路径、二进制指纹和固定参数必须匹配。逐包trace解析必须核实字段布局与事件语义，并核对包数、字节、路径、重复与丢弃。trace开启后的8MB仿真时间应与已存基线相同，否则先调查，不能据其归因。

如果有候选优化，原版和候选分别两遍运行，在8/2/4及至少一个对照拓扑测试；改动清单和所有不改善结果均保留。记录测试使用PYTHONPATH=src;D:/codex/集合通信仿真26暑/.test-deps，D:/python/python.exe -B运行render_ara_graph.py、validate_ara.py、tests/test_ara.py及tests/test_ara_visualization.py。原始记录不进Git。

## Surprises & Discoveries


实际common.h的nbr2if只用两个节点作为键，同一对节点的平行链路逐次覆盖idx，SetRoutingEntries因此只安装最后接口。正向显式alias路由绕过此缺陷；ACK目的为原始GPU地址，仍受影响。实际构建头文件SHA256为2a08f0a225102c945f266bef4bcf07c2956f4ace9bb88a0c81ac0c0127211f73，证据副本在outputs/clos_diagnosis_20260916/common_header_actual.h。

8/2/4最忙链路141764ns数据发送+7879ns ACK=149643ns，8/4/2同数据发送+5009ns ACK=146773ns。不是正向链路普遍打不满；FCT的QP任务start_time为0，未观察到逐个延迟提交，但各QP首包仍可能等待链路服务。CC_MODE=12在当前ReceiveAck代码无速率调整分支，不称为已证明的拥塞控制降速。

## Decision Log


2026-09-16：用户把优先级从继续接入改为当前结果做扎实；新增本计划承接，不回写历史报告伪装方向未变化。保留理论分母，不以改带宽、数据量、关协议开销实现所谓优化。

2026-09-16：允许在独立配置内补齐ACK普通最短路遗漏接口；这修正路由可见性，不减少ACK或PFC。未修改bridge或ASTRA核心源码，不拉取新版本，所有旧结果仍代表原配置。Q1作为不应改变的负对照，32/2/2作为更大规模回归。

## Idempotence and Recovery


每次运行新目录，失败保留。不得覆盖旧trace或替换原始哈希。先检查tmux与内存避免重复运行。不改安全组或云配置，不删除服务器产物，不修改子仓源码。若必须改仿真器，先报告证据及所需授权。

## Artifacts and Notes


本地输出outputs/clos_diagnosis_20260916；本计划同目录保存RESULTS.md。远程实验父目录为/home/mcnfsim/mcnf-smoke/experiments。

原配置诊断批clos_diagnosis_20260916_Y5QyUr已完成8次；压缩包SHA256 a38770a142ca6fec33ece673a7368d326fb9f02f03867668d160bcb60c627e2a，两端一致。修正候选批clos_ack_candidate_20260916_HWL1Gq已完成4配置8次；压缩包SHA256 5a2b0d08a0328c6573a11385edf16687d1ebb9a77d6b7e8adee03882e4270b8d。

外层脚本run_diagnosis.py/.sh与run_ack_candidate.py/.sh；纯输入函数ack_routes.py含Q1/Q2/Q4/32卡测试、18个篡改负例及重复应用拒绝；独立分析analyze_trace.py、gap_static.py、audit_diagnosis.py。失败审查见failure_recovery.md。大型trace留在输出目录，不纳入Git。

## Interfaces and Dependencies


复用scripts/run_clos_qp_benchmark.py的输入生成、原生仿真、轨迹字段以及当前缓存ELF；新增外层诊断工具不改变正式benchmark默认行为。无需安装依赖。

## Outcomes & Retrospective


本轮16次新运行全部完成并通过相应独立验收，找到ACK回程遗漏并验证候选改善；近期两次失败的同配置恢复证据已核实。两名独立审阅者确认数字与科学边界，已细化QP开始时刻、有效载荷和PFC计数措辞。未把候选合入默认实现，不推进新拓扑；正式集成与更广回归仍留待后续。

更新说明：2026-09-16，本轮差距定位、隔离候选对照、失败恢复核验及归档已完成；后续继续在当前阶段做正式集成与更多回归，不将本轮结束写成整个项目完成。
