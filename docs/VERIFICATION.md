# 本地验证记录

验证日期：2026-11-08。执行环境：macOS，Python 3.15.0。

## 已通过

- `python3 -m unittest discover -s tests -v`：14 项测试通过。包括有效状态、只读性、身份不一致、修订号、类型异常、无效 owner gate 引用、无效状态拒绝聚合、时区、缺文件/坏 JSON/非 UTF-8、显式盘点范围与外部符号链接排除、CLI 错误码、任务数量/唯一性/优先级/主子身份约束，以及 owner gate 无法覆写来源项目身份。
- `python3 -m compileall -q scripts tests`：脚本和初始测试编译通过；最后新增测试由 unittest 实际导入并运行。
- `python3 scripts/demo.py`：虚构临时项目状态校验成功，输出一个负责人决策事项，临时文件由上下文管理器清理。
- `python3 scripts/capability_index.py --root ./examples --format json`：空示例目录输出空清单，未触发默认个人目录扫描。
- 初轮 15 个候选文本文件的特定个人路径、业务名称、私钥头及常见密钥形态关键词检查：无命中。测试运行生成的字节码不属于候选文件。
- 抽取源文件与 SOURCE_REVIEW.json 的 SHA-256 核对：全部相同，已安装源 Skill 未改动。

## 未验证

本地验证阶段未运行跨操作系统/Python 版本矩阵、专用凭据扫描或真实宿主任务闭环。关键词检查不能证明绝无秘密。此记录描述发布前检查；远程 CI 结果以 GitHub Actions 为准。

独立只读复核发现收件箱合并顺序允许 gate 字段覆盖项目身份，已修复并补充回归测试。最终 14 项测试通过。

## PMOP 候选复验（2026-11-08）

- 14 项 unittest 再次通过，虚构临时项目 Demo 再次通过。
- Codex CLI 0.145.0 的版本、exec/resume 帮助实测可读；未运行真实子任务闭环。
- Hermes 本机源码 aaa863f7ff 的 delegate_task schema 与后台生命周期说明已读；CLI 资产请求被策略阻止，未绕过。
- 新增 CI 配置只是待运行配置，不算跨系统验证证据。
- 发布前 GitHub 账户连接已验证。维护者随后确认原创并授权以 PMOP 名称公开，采用 MIT 许可证。

## 首轮远程 CI 修正

首轮 Linux/macOS 通过，Windows 暴露 Demo 使用系统默认编码读取中文模板的问题。改为显式 UTF-8 文件读写，三个 CLI 的输出也统一 UTF-8，并增加强制 ASCII 环境下的 Demo 回归测试。修复后的完整矩阵结果以 Actions 对应提交为准。
