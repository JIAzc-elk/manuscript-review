@AGENTS.md

# Claude Code adapter

Claude Code discovers the Manuscript Review entry Skill at `.claude/skills/manuscript-review/SKILL.md` and the seven specialist adapters at `.claude/agents/`.
The Claude Skill is only a discovery wrapper; `.agents/skills/manuscript-review/SKILL.md` remains the canonical runtime router.
Chairman stays on the main conversation. Resolve each formal Stable Agent ID through the hyphenated Claude Code host alias (for example `story_plot_structure` → `story-plot-structure`) before delegation.
