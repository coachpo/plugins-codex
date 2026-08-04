# plugin-codex

CoachPo 的 Codex 插件 marketplace，用于发布可复用的项目工作流。

## Project Workflow

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
codex plugin add project-workflow@coachpo-plugin-codex
```

安装或更新后，请新建 Codex 任务以加载插件技能。

## 仓库结构

```text
.agents/plugins/marketplace.json
plugins/project-workflow/
├── .codex-plugin/plugin.json
└── skills/
    ├── draft-consensus-goal/
    ├── init-deep/
    ├── start-consensus-goal/
    └── write-project-docs/
```

## License

[MIT](LICENSE)
