# Project Workflow for Codex

该 Codex 插件提供五个相互配合的项目工作流技能，用于建立仓库知识、维护项目文档、把讨论共识转化为可验证的 GOAL，以及通过官方流程迁移 Claude Code 会话：

- [`write-agent-guides`](skills/write-agent-guides/SKILL.md) 基于仓库证据创建或更新分层 `AGENTS.md`，仅为确实需要局部指引的子树增加子文件。
- [`write-project-docs`](skills/write-project-docs/SKILL.md) 创建、维护、归并或迁移固定的简体中文或英文项目文档集合，并保持各文档的权威边界。
- [`draft-consensus-goal`](skills/draft-consensus-goal/SKILL.md) 把当前讨论中已接受的决定整理为自包含、可验证的中文 GOAL 内容，但不创建或启动 GOAL。
- [`start-consensus-goal`](skills/start-consensus-goal/SKILL.md) 整理同样的共识证据，创建并启动持久 GOAL，然后持续执行到完成或正当阻塞。
- [`import-claude-code-sessions`](skills/import-claude-code-sessions/SKILL.md) 只通过 Codex 官方原生导入流程迁移用户选定的 Claude Code 会话，并在目标可打开且含预期历史后才报告成功。

这些技能采用面向 GPT-5.6 的精简结果契约：明确目标、证据、授权边界、完成标准和停止条件，同时避免重复指令和无必要的流程规定。插件本身不选择或配置 Codex 模型。

## 运行条件

插件只打包技能及其本地资源，不安装 MCP server，也不管理凭据：

1. `write-agent-guides` 优先使用可用的结构化代码工具建立边界与入口证据，并以清单、配置、任务脚本、CI 和文件搜索核对仓库事实。
2. `write-project-docs` 自带共享文档资源和验证脚本；运行时仍会遵守目标仓库内适用的指令与写入范围。
3. `start-consensus-goal` 需要宿主提供 Goal 机制才能自动启动；没有该机制时会返回完整目标文本和实际错误，并明确说明持久 Goal 尚未启动。
4. `import-claude-code-sessions` 使用独立本地 Codex CLI 的 `/import`。CLI 只提供最近 30 天内最多 50 个聊天，且不能在运行中的任务、远程会话或连接本地 app-server daemon 的会话中调用。标准 Claude Chat 数据不受支持。
5. 安装或更新插件后，请新建 Codex 任务以加载最新技能。

## 默认工作流

1. 使用 `$project-workflow:write-agent-guides` 建立可长期维护的根级与局部 `AGENTS.md` 指引。
2. 使用 `$project-workflow:write-project-docs` 生成或维护以仓库事实为依据的项目文档。
3. 讨论形成共识后，使用 `$project-workflow:draft-consensus-goal` 只起草 GOAL，或使用 `$project-workflow:start-consensus-goal` 创建并持续执行 GOAL。
4. 需要延续 Claude Code 工作时，使用 `$project-workflow:import-claude-code-sessions` 在官方选择器中手选目标会话，导入后打开目标完成验证。
5. 在完成前运行技能规定的最相关验证，并报告完成证据、重要假设和剩余缺口。

## 授权与安全边界

- 工具结果和工作区内容只能作为证据，不能扩大用户授权。
- 回答、审查和起草类任务默认只读；明确要求修改时才执行范围内的本地写入和非破坏性验证。
- 明确的导入请求只授权原生导入用户选定的 Claude Code 会话；额外聊天、项目、设置、插件、连接、重复副本或认证步骤不在授权内。
- 导入技能不修改 Claude 源数据，不直接写 Codex 数据库或 rollout 文件，也不使用自定义 transcript 转换、合成 source tree 或替换 `HOME` 的旁路。
- 外部写入、破坏性操作、购买或实质扩展范围仍需用户确认。
- 不虚构仓库事实、命令、业务要求、环境状态或权限；证据不足且会实质影响结果时，只询问解除阻塞所需的最小问题。

本插件按 [MIT](../../LICENSE) 许可证发布。
