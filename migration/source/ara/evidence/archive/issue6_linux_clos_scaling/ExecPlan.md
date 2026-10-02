---
status: complete
owner: codex-local
last_verified: 2026-09-16
scope: 固定版本单层Clos的8/16/32卡扩规模验证，不改仿真行为
---

# 扩大 Linux 单层 Clos 基准规模


本计划按 `docs/guideline/PLAN.md` 维护，接续 Issue #6/#9 已有实验。不创建外部 Issue、PR，不提交、推送或修改仿真器、求解器和桥接核心。昨天的未提交研究记录属于用户工作，完整保留。

## Purpose / Big Picture


昨天仅验证四个小拓扑。今天在同一服务器、同一源码和二进制、同一物理参数下扩大卡数，判断是否具备接入真实求解方案的基础。通信任务仍为手工构造的全互发，不是求解器生成的 Allreduce。完整225组合、双层Clos、UBMesh和求解器接入不作为本次已经完成的工作。

## User Raw Prompts


“不用花那么多时间准备材料，干活更重要，单层的CLOS复现完了没有？”

“单层复现完然后就搞双层，最后弄ubmesh之类的，师兄看完结果对照之后说了一句：可以再试试大点的，没问题了就可以接我们求解器了，根据这些安排，出一个接下来的计划，包括明天干什么、后天干什么、周五要汇报什么、接下来的规划和安排大致如何。”

2026-09-16 用户“开始干活”，授权执行昨天确定的扩规模实验。优先增加规模，不以先补齐全部R=2/4或225组合为进入下一阶段的必要条件。

## Progress


- [x] 2026-09-16：阅读实验/远程/研究规范、全局研究图和昨日计划，核对本地修改仅为已有研究归档。
- [x] 2026-09-16 10:57 CST：SSH确认服务器代码仍为1d4f816，约29827MiB可用内存、88GiB可用磁盘，无仿真占用，tmux可用。
- [x] 2026-09-16 11:05 CST：首批6配置分别重复两遍：N=8/16/32、M=2、Q=1/2、R=1。
- [x] 2026-09-16 11:07 CST：首批独立验收PASS，0错误/0缺失；25760条FCT与25760个校准QP路径全部核对，正式qp_config与校准及实际FCT对应。
- [x] 2026-09-16：追加5配置10次完成，extended_ftlIDF独立验收PASS；两批合计41184条FCT及41184个校准QP路径核对通过。
- [x] 2026-09-16：结果报告及ARA更新完成；全局图重建、结构校验通过（39节点、58边、36证据、13结论、6会话）；19项记录测试通过，独立最终报告审阅PASS。

## Context and Orientation


服务器116.205.103.45上的已有工作目录为 `/home/mcnfsim/mcnf-smoke`，普通用户mcnfsim运行仿真。bridge子目录固定commit为 `1d4f816a542f46ff0d1c99af6ce2d8b097822303`，`repos/astra-sim` 固定为 `181c7856ed77bac3be68495e2400752488df5e5a`。Python为 `server-smoke-kit/.venv-linux/bin/python`，protobuf C++库路径 `/usr/lib/x86_64-linux-gnu`。已有二进制SHA256为 `7f9db19d50dafbe8d371c9f64cbef8b9e7b27cb7794fb1c62e6be8956ade67f4`。

N为卡数，M为并行交换机数，Q为每张卡到每台交换机的平行链路数，R为每条完整物理路径上的发送通道(QP)数。所有案例每对卡单向8000000字节、每条链路400Gbps/500ns、4096字节小包、R=1、均匀分配。理论时间为160*(N-1)/(M*Q)微秒。只改N/M/Q，不改协议、包大小、延迟和带宽。

## Plan of Work / Milestones


第一阶段运行8/16/32卡各M=2、Q=1/2。每个配置先first再repeat，验证该档稳定后升档。每遍独立目录，避免昨天发现的校准覆盖问题。每条命令最长600秒、只使用CPU0-7、单进程虚拟内存上限12GiB；启动前可用内存不足8GiB则不启动下一个配置。宿主time-v峰值不等于整机总内存峰值。

第二阶段对首批进行独立验收。大于8%的差距保留为结果并审查，不视为删除案例或调整参数的理由。若结果合理且资源充足，新增(8,4,1)、(8,4,2)、(16,4,1)、(16,4,2)、(8,2,4)，各重复两遍。

第三阶段归档所有成功、失败或资源保护终止的实验，保存结果与其原始证据。只根据已验收配置描述扩展能力，不宣布整个单层Clos或求解器接入完成。

## Concrete Steps


本地包装脚本为 `D:/codex/集合通信仿真26暑/outputs/clos_scaling_20260916/run_scaling.sh`。经scp复制到服务器同日独立脚本路径，核对SHA256、bash -n后，在mcnfsim的tmux会话运行：

    bash /home/mcnfsim/mcnf-smoke/run_clos_scaling_20260916_v2.sh core

实际成功脚本为 `run_clos_scaling_20260916_v2.sh`，SHA256 `1dd34977c20d521004c1f23f181e5377cac27c5189f0fa586504bd278ee96a70`，修正了初版外层检查字段名。核心批次是 `clos_scaling_20260916_core_8QrZpA`。追加批在11:07 CST以同一v2脚本extended参数启动，已完成于 `clos_scaling_20260916_extended_ftlIDF`。

脚本自动新建 `experiments/clos_scaling_20260916_core_XXXXXX`，每次运行保持独立。扩展批次使用同一脚本的 `extended` 参数，会新建另一目录。执行现有 `scripts/run_clos_qp_benchmark.py`，不改repo脚本。日志留在批次console.log和resources目录，保存time-v、可用内存、实际命令、原始案例与校准trace。

## Validation and Acceptance


每行status成功，FCT条数与活跃QP数量相同，累计传输字节为N*(N-1)*8000000，每张卡完成。独立复算理论与差距；两遍仿真完成时间应相同，包数均匀分配差不超过1。校准trace引用哈希必须对应实际文件，重新解析逐跳路径。正式性能案例仍关闭全包trace，不能把校准路径证据冒充正式每个包的轨迹。核对二进制实际SHA256及输入配置，记录PFC和错误日志。

拉回当前批次结果与日志，不覆盖本地源码或昨日输出。结构校验使用 `PYTHONPATH=src python scripts/validate_ara.py`；更新全局图后生成HTML并运行相关测试。原始日志不提交到Git。

本地D:/python环境首次直接运行缺少yaml/pytest；不安装或更改依赖，沿用工作区已有.test-deps加入PYTHONPATH后完成验证。实际PowerShell环境为 `PYTHONPATH=src;D:/codex/集合通信仿真26暑/.test-deps`，运行render_ara_graph.py、validate_ara.py以及tests/test_ara.py、tests/test_ara_visualization.py，结果19 passed。

## Surprises & Discoveries


首批 `clos_scaling_20260916_core_86J6hV` 在首个8卡案例成功生成结果后，外层内联检查误用 `size_bytes` 而实际汇总字段为 `size_bytes_per_pair`，触发KeyError并停止。保留原批和原脚本，不作为完整批次验收。只修正外层字段访问，上传v2脚本并新建目录重跑。昨天四小配置及历史微差结论保持不变。

独立审阅发现旧验收覆盖plan/children和校准trace，但尚未核对正式ASTRA实际读取的qp_config。新版只读验收补齐正式/校准QPs/routes相等、messages与children守恒、每条FCT对实际child的端点/IP/端口/字节匹配以及两遍qp_config字节相等。此前原始产物未改写，昨日rr八条case和路由/字节/端口内存篡改负例通过该验收工具测试。

32/2/2每遍出现312条PFC原始事件，其余新增配置为0；两遍仿真时间1293.096us、差距4.28194%。根据实际构建源码核对，312条为156条收到暂停和156条收到恢复，不是312次暂停或丢包。它表明触发过缓冲阈值流控，但正式性能未开全包trace，不声称已量化流控对完成时间的贡献。

追加8/2/4的差距为8.36714%，两遍相同，独立输入与结果审计通过；该配置PFC为0。与相同理论时间的8/4/2相差2.859us，尚未隔离具体原因，不把它归因于32卡的PFC现象。

## Decision Log


2026-09-16：继续使用已有Issue6记录分支和固定服务器源码，不拉取新版本混入性能对比；不给原始研究记录做清理或重置。

2026-09-16：优先N扩规模，再增加M/Q。将R=2/4和全225组合后置，与用户和师兄新确定的优先级一致。

2026-09-16：复用既有远程工作目录而不是迁移到规范默认路径，避免重复安装和破坏昨日可复现环境；新实验仍以独立目录隔离。

## Idempotence and Recovery


启动前检查同名tmux会话，不并行重复跑同批。脚本失败保留全部目录，先定位失败再新建运行；不回写旧summary、trace或哈希。网络失败只核查既有连接，不擅自扩大SSH来源白名单。不删除远程产物。

## Artifacts and Notes


本地结果根目录为 `D:/codex/集合通信仿真26暑/outputs/clos_scaling_20260916`，报告放在本计划同目录RESULTS.md。远程同名批次均位于 `/home/mcnfsim/mcnf-smoke/experiments/`。昨日结果位于独立的 `outputs/clos_reproduction_20260915`，仅作参考不覆盖。

核心批及失败批压缩包SHA256为 `65b5fd3f971f38c06bab4e71a32c1563aafe73ad61c7c91b3c333cc4ba52c938`，服务端与本地相同。验收命令：

    D:/python/python.exe -B outputs/clos_scaling_20260916/analyze_scaling.py outputs/clos_scaling_20260916/clos_scaling_20260916_core_8QrZpA --bridge-root mcnf-sim-bridge

验收脚本复用旧FCT/校准审计函数，新加可变配置清单、真实配置检查与原生轨迹复解析，输出scaling_audit.json/.md，不修改输入。

追加批压缩包SHA256为 `26572ff6c4278cb0044439e03dccab242f11738c918feb6a6bde06b1d7f1e616`，两端一致；同一验收命令替换为extended_ftlIDF目录后亦PASS。

## Interfaces and Dependencies


不安装新依赖。沿用现有Python、ASTRA、tmux、timeout和time；只新增外层运行/验收脚本与研究记录。已有校准和独立结果校验可复用，均不改变仿真行为。

## Outcomes & Retrospective


核心批6配置12次与追加批5配置10次均已通过独立验收，每个配置两遍逐纳秒一致。核心批差距2.9975%～5.175%，合并本批范围为2.9975%～8.36714%，10/11低于8%。22次time-v命令耗时合计305.76秒，最大MaxRSS253748KiB，不是整机总峰值。没有修改仿真核心或协议参数；不能宣称全225组合、无流控或求解器已接入。

更新说明：2026-09-16，固定版本扩规模验证完成；已归档原始失败、11配置22次正式运行、完整输入/原生轨迹核验、两项待诊断现象及独立报告复核。下一阶段为最小真实求解结果接入准备，不将本轮结果等同于算法实际优势验证。
