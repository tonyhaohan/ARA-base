# ARA Base

可继承、可按部分抽取的自动研究记录基准。Issue 概览和 idea 细节各有一层 DAG；研究纪要按需读取，失败、证据和结论形成过程都可追踪。

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python3 scripts/ara.py validate
python3 scripts/ara.py render
python3 scripts/ara.py issues
python3 scripts/ara.py ideas
python3 scripts/ara.py show I000-N00
python3 -m unittest discover -s tests -v
```

打开 `ara/views/index.html` 查看双层研究地图。`main` 保留干净的初始 artifact（只有虚拟根）；真实 bridge 历史放在 [`codex/issue2-bridge-history`](https://github.com/tonyhaohan/ARA-base/tree/codex/issue2-bridge-history) 分支。切到示例分支后，用 `python scripts/ara.py issue 5` 查看总结及两组重点 idea，用 `python scripts/ara.py read I003-N01` 提取单个章节。已有 `.venv` 时直接激活复用。只检查页面是否最新使用 `render --check`，不会改写文件。

## 自动生成 HTML

在项目根执行 `python scripts/ara.py render`，脚本读取当前 YAML 索引、研究纪要及证据记录，从复用模板 `scripts/viewer.html` 生成 `ara/views/index.html`。节点、依赖、重点 idea 和纪要内容都来自研究记录，无需逐次手写页面。

`ara/views/index.html` 是生成产物，不直接编辑。数据更新后重新运行脚本；CI 的 `render --check` 会拒绝与数据或模板不一致的旧页面。

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
