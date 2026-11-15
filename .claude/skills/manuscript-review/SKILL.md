---
name: manuscript-review
description: "正文审核器：当用户提供小说正文（章节/片段）以及可选的设定、人物卡、大纲、前文、文风样本、读者反馈等任意素材，要求评价章节质量、找问题、给修改意见或判断“这章能不能发”时使用。若用户只给正文且未说明素材情况，先问一次是否有设定/人物卡/大纲/前文；用户确认没有后再按纯文本模式审。组织多个专业角色多轮讨论，最终只输出一份审核报告，绝不修改用户提供的任何文件。不用于代写正文、续写、直接改稿或设定创作。"
compatibility: "Multi-host compatibility discovery adapter; canonical runtime router remains .agents/skills/manuscript-review/SKILL.md"
---

# 正文审核器 — 多宿主发现适配器

本文件只是让扫描 Claude 兼容 skill 目录的宿主发现本 skill，**不是**运行时权威，也不复制主控逻辑。

如果这段适配器文字已经出现在当前会话中，不要再调用一次 `manuscript-review`，不要 glob/search 另一个 `SKILL.md`，也不要先枚举用户项目文件。直接读取 canonical 主控文件：

`../../../.agents/skills/manuscript-review/SKILL.md`

在执行任何审核动作前，必须完整读到该文件的 `<!-- MANUSCRIPT_REVIEW_ROUTER_EOF: manuscript-review -->`。如果输出被截断，继续分段读取；无法建立连续覆盖时返回：

`MANDATORY_LOAD_INCOMPLETE: ../../../.agents/skills/manuscript-review/SKILL.md`

相对路径以 canonical 文件所在目录为基准解析。角色契约在 `../../../.agents/skills/manuscript-review/roles/`，运行规则在 `runtime/`，模板在 `templates/`。不要在本适配器中总结、改写或替代 canonical 权威。

Claude Code 的七个专业子代理在 `.claude/agents/`，使用连字符宿主名（例如 `story-plot-structure`），但圆桌归属以 Stable Agent ID（例如 `story_plot_structure`）为准。
