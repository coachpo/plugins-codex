# plugin-codex

CoachPo 的统一 Codex 插件 marketplace，从一个 GitHub 仓库发布 UI/UX 设计与项目工作流插件。

## 插件

### Stitch UI/UX for Codex

`stitch-ui-ux-codex` 提供五个适配 Codex 的 UI/UX 技能，用于提示词完善、Stitch 屏幕生成与编辑、设计系统提取、多页面迭代和 React 交付。插件原样保留，仍需单独配置官方 Google Stitch Remote MCP。

详细说明见 [`plugins/stitch-ui-ux-codex/README.md`](plugins/stitch-ui-ux-codex/README.md)。

### Project Workflow

`project-workflow` 将仓库知识、项目文档和共识目标工作流打包为一个插件：

| Skill | 用途 |
| --- | --- |
| `project-workflow:init-deep` | 基于仓库证据创建或更新分层 `AGENTS.md`。 |
| `project-workflow:write-project-docs` | 创建、维护或迁移固定的中文项目文档集合。 |
| `project-workflow:draft-consensus-goal` | 将当前讨论中的已接受决定整理为 GOAL 内容，但不启动。 |
| `project-workflow:start-consensus-goal` | 将当前共识整理为 GOAL 并启动持续执行。 |

## 安装

```bash
codex plugin marketplace add coachpo/plugin-codex --ref main
codex plugin add stitch-ui-ux-codex@coachpo
codex plugin add project-workflow@coachpo
```

安装或更新后，请新建 Codex 任务以加载插件技能。

## 从旧 marketplace 迁移

旧安装分别来自 `coachpo` 和 `coachpo-plugin-codex` 时，先移除旧插件与 marketplace，再安装统一仓库：

```bash
codex plugin remove stitch-ui-ux-codex@coachpo
codex plugin remove project-workflow@coachpo-plugin-codex
codex plugin marketplace remove coachpo
codex plugin marketplace remove coachpo-plugin-codex
codex plugin marketplace add coachpo/plugin-codex --ref main
codex plugin add stitch-ui-ux-codex@coachpo
codex plugin add project-workflow@coachpo
```

## 仓库结构

```text
.agents/plugins/marketplace.json
plugins/
├── stitch-ui-ux-codex/
│   ├── .codex-plugin/plugin.json
│   └── skills/
└── project-workflow/
    ├── .codex-plugin/plugin.json
    └── skills/
        ├── draft-consensus-goal/
        ├── init-deep/
        ├── start-consensus-goal/
        └── write-project-docs/
```

## 许可证

- 仓库整合内容与 Project Workflow：[`MIT`](LICENSE)
- Stitch UI/UX for Codex：[`Apache-2.0`](plugins/stitch-ui-ux-codex/LICENSE)，并保留其 [`NOTICE`](plugins/stitch-ui-ux-codex/NOTICE)、[`THIRD_PARTY_NOTICES.md`](plugins/stitch-ui-ux-codex/THIRD_PARTY_NOTICES.md) 和 [`UPSTREAM.md`](plugins/stitch-ui-ux-codex/UPSTREAM.md)
