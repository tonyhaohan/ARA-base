# Issue #2 — 迁移集成与记录系统验收

## 统一信息

本Issue记录2026-10-02实际进行的迁移与验证。原研究事实属于源Issue3/6/9，本Issue结果只评价记录系统。

```yaml
source_graph_commit: 9e2058fcca7b95389d30e81cb0e52ffe03e2e930
conditions_status: complete
environment:
  python: 3.14.2
  yaml: 6.0.3
config:
  source_issues: [3, 6, 9]
  destination_issues: [3, 4, 5]
  simulations_rerun: false
```

## I002-N01 保留原始事实并建立两层独立索引

```yaml
overrides: {}
evidence: [E002-01]
```

### choice

统一将原next反推为前置依赖并合并also_depends_on；保留全部跨Issue边，主要依赖由迁移者说明理由。Issue概览另行归纳，正文按idea提取，原材料冻结保留。

### alternatives

- 把Issue边从idea边机械压缩，会把交错研究变成Issue环。
- 只复制文字而不校验源节点和边，无法证明迁移完整。

### limitations

历史作者未指定主要依赖；新选择是索引解释。缺少原始trace的历史报告不能据此升级为本次实验复现。

## I002-N02 按冻结源逐字段验证迁移和按需读取

```yaml
overrides: {}
evidence: [E002-02]
```

### hypothesis

迁移后的活动图与所选历史子图在真实节点、前置依赖及原始正文上保持一致，单个idea可以只携带公共条件和自身章节读取。

### method

执行 `python migration/check_import.py` 比较所有源节点的身份、类型、状态、来源、时间、证据和正文；比较完整边集合；逐文件验证源材料SHA256；逐一提取43个idea检查没有相邻章节泄漏。另执行仓库测试、GitHub实际linked branch校验及浏览器交互检查。

### result

43个idea、63条真实依赖、149个原文字段一致；48份冻结源文件SHA一致；43次独立提取均只包含目标章节。核心测试与实际GitHub关联校验通过。浏览器可由Issue重点列表进入idea、查看前置和自动反推后继、展开公共条件和自身纪要，无JavaScript错误。

### limitations

本次验证覆盖结构、已取得的归档材料和读取行为。没有运行旧仿真实验，不证明原始数字可在当前环境重现。原始运行数据缺失已逐证据标记。
