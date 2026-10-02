# bridge 早期研究迁移样例

入口：`ara/views/index.html`。活动artifact含原Issue3/6/9的43个idea（映射到新Issue3/4/5），另有Issue2的两个迁移验收节点。main保留干净的空研究起点。

```sh
python scripts/ara.py issue 5
python scripts/ara.py read I005-N17
python scripts/ara.py show I005-N17
python scripts/ara.py validate --github
python migration/check_import.py
python scripts/ara.py render --check
```

`VALIDATION.json`是逐字段审计结果；`SOURCES.md`说明来源，`source-manifest.json`是冻结源内容校验值。`reviews/`记录三个无上下文迁移worker与新读者的测试，协议已根据反馈改进。

所有43个历史idea的类型、状态、原始正文和63条前置边保留。两层图并不逐边对应。当前最佳/潜力列表和主要依赖是迁移者的索引判断，理由可查。

原始运行、完整trace和历史二进制未重跑或重建。当前验证证明记录结构和归档文本一致，不证明原数字重新复现。
