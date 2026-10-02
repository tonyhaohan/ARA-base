---
status: active
owner: core-maintainers
last_verified: 2026-07-11
scope: Issue #6 显式完整路径与 persistent QP 的 N/M/Q/R 粗扫结果
---

# 显式完整路径 N/M/Q/R 粗扫

## 结论

新路线走得通。bridge 显式生成 edge path 和逐跳 interface 后，不再需要搜索 host/switch hash 的 source-port preimage。Q=2 时每个 switch 的两条入链路与两条出链路形成四条完整路径，native trace 已逐条验证。

代表性 12 个真实 ASTRA/ns-3 case 全部成功。理论差距为 3.83%--9.37%；同一 topology 中 R=2/4 相对 R=1 的最大绝对变化为 0.79%，没有稳定容量收益。默认应使用每条完整路径一个 QP，即 R=1。

## 口径

- N：GPU 数；
- M：switch 数；
- Q：每个 GPU-switch pair 的平行物理链路数；
- R：每条完整物理路径的 QP 数；
- 每个 endpoint group size：`M*Q^2*R`；
- 每个有向 GPU pair：8,000,000B，4096B message hash；
- 理论时间：`160*(N-1)/(M*Q) us`。

## 结果

| N | M | Q | R=1 (us) | R=2 (us) | R=4 (us) | theory (us) | 最大相对 R=1 变化 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 166.208 | 166.135 | 166.135 | 160.000 | 0.04% |
| 2 | 1 | 2 | 86.909 | 86.220 | 86.219 | 80.000 | 0.79% |
| 4 | 2 | 1 | 255.585 | 256.559 | 255.757 | 240.000 | 0.38% |
| 4 | 2 | 2 | 131.249 | 131.149 | 131.067 | 120.000 | 0.14% |

全部 case 的 FCT 行数与实际承载数据的配置 QP 数一致，总字节守恒，PFC event 为 0。校准 trace 对每个 topology 的 max-R plan 验证所有 QP 的 source、switch 和 destination interface；正式 case 使用同一 plan 的子集。

## 单独的 reuse 证据

`scripts/run_qp_reuse_smoke.py` 在同一个 QP 上顺序发送两个 1 MiB message。两行 FCT 使用相同 destination alias `12.0.1.1` 和 source port `10000`；第一段为 23.333us，第二段从 23.333us 开始并再运行 23.333us，总 wall time 46.666us。这证明 adapter 复用已有 QP sequence，而不是为第二个 message 换端口创建独立路径。
