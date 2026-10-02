# ARA Base

可继承、可按部分抽取的自动研究记录基准。Issue 概览和 idea 细节各有一层 DAG；研究纪要按需读取，失败、证据和结论形成过程都可追踪。

```sh
python3 -m pip install -r requirements.txt
python3 scripts/ara.py validate
python3 scripts/ara.py render
python3 scripts/ara.py issues
python3 scripts/ara.py ideas --issue 3
python3 scripts/ara.py read I003-N01
python3 -m unittest discover -s tests -v
```

打开 `ara/views/index.html` 查看双层研究地图。`main` 保留干净的初始 artifact（只有虚拟根）；真实 bridge 历史将放在独立的 Issue 分支。

## 使用与抽取

- 新研究项目可以直接使用 GitHub 的 Use this template；修改 `ara/project.yaml` 的项目名与仓库地址。
- 现有项目只需复制 `scripts/`、`requirements.txt`、`ara/`、`docs/PROTOCOL.md`、`docs/NOTES.md` 和研究技能，并将 AGENTS 的研究入口加入原有说明。不要覆盖原项目已有规范。
- GitHub Issue、研究分支与 ExecPlan 一一对应，命名为 `codex/issue123-topic`，用 `gh issue develop` 创建关联，再用 `--list` 核验。
- 研究任务开始先查两层索引；每次有实质进展追加 session；Issue 收尾填写总结中的两组重点 idea。
- 文件格式与校验边界见 [PROTOCOL](docs/PROTOCOL.md)，纪要和配置继承见 [NOTES](docs/NOTES.md)。

工具只有一个运行依赖 PyYAML，不需要数据库、前端工程或模型 API。HTML 可离线查看。GitHub 实际关联另用 `validate --github` 核验；结构检查通过不等于实验复现成功。

本仓实现受 [ARA](https://arxiv.org/abs/2604.24658) 启发，并对 DAG、GitHub 工作流和研究纪要做了适配；不宣称与官方 ARA schema 直接兼容。

updated at 2026/10/02
written by codex local
