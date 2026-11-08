# PMOP

用项目本地的两份 JSON，保存主编排身份、当前结果、任务路由和需要负责人决策的事项。协议负责约束协作，Python 工具负责结构检查和生成只读收件箱。

PMOP 是宿主无关的项目编排协议与只读辅助工具。以 MIT 许可证开源，目前处于实验阶段。原有 Skill 和业务项目未被修改。

## 一分钟试用

需要 Python 3.10+，只使用标准库，无需安装依赖。在本目录运行：

```sh
python3 scripts/demo.py
python3 -m unittest discover -s tests -v
```

Demo 创建临时的虚构项目，校验其状态并打印一个待决策事项，然后清理临时目录。不读取现有项目或主机配置。

检查自行准备的项目：

```sh
python3 scripts/orchestration_state.py validate --root /absolute/project/root --json
python3 scripts/orchestration_state.py owner-inbox --root /absolute/project/root --format json
python3 scripts/capability_index.py --root ./examples --format json
```

第三条仅盘点显式目录中的 SKILL.md 文件，不读取 Codex 配置或运行 MCP。盘点结果含相对文件名，应按私有资料管理。安装、启用状态与当前会话可见工具仍需宿主单独核实。

## 宿主适配状态

- Codex：已核实本机 CLI 版本及 exec/resume 接口；提供人工接入适配说明，未完成真实任务闭环。
- Hermes：已核实本机 delegate_task 源码接口；提供会话内子任务适配说明，未完成真实任务闭环。
- Claude：仅规划，尚未验证接口或运行。

这些是协议适配说明，不是自动执行连接器。详见 [适配契约](adapters/README.md)、[Codex](adapters/codex.md) 和 [Hermes](adapters/hermes.md)。

## 组成

- SKILL.md：接单、路由、交接、验收、归档与主编排接续。
- references/：主编排身份、运行状态和任务交接契约。
- templates/：虚构的初始控制文件，默认手动开子任务、提交需确认。
- scripts/：只读校验、跨项目收件箱、显式范围能力盘点，以及临时演示。
- tests/：标准库 unittest 回归测试。
- docs/：来源核查、抽取说明和发布前检查。

模板里的路径与线程 ID 都是占位符，接入前必须替换，不能作为真实运行证据。不要把真实控制状态、任务历史、配置、凭据或能力盘点结果加入待发布文件。

## 边界

这是协议和本地辅助工具原型。它不创建任务、不执行代理、不后台调度、不实施权限控制，也不自动同步项目。JSON 校验通过只代表所覆盖的结构检查通过，不能证明任务完成、授权有效或证据真实。单写者、修订检查和权限停点仍由宿主落实。

## 许可证

[MIT](LICENSE) · Copyright (c) 2026 dlxeva。维护者已确认原始 Skill 为原创并授权开源。来源核查与验证边界见 [发布审查](docs/RELEASE_REVIEW.md)。
