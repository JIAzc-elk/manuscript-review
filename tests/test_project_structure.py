#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目结构自检（只读）。

运行：
    python3 -m unittest discover -s tests -v

不修改任何文件；只检查 skill 文件、角色契约、宿主适配层与示例报告。
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "manuscript-review"

ROLES = [
    "character",
    "story_plot_structure",
    "scene_dialogue",
    "story_deconstructor",
    "devil_critical_review",
    "secretary",
]

CLAUDE_NAMES = {
    "character": "character",
    "story_plot_structure": "story-plot-structure",
    "scene_dialogue": "scene-dialogue",
    "story_deconstructor": "story-deconstructor",
    "devil_critical_review": "devil-critical-review",
    "secretary": "secretary",
}


class StructureTests(unittest.TestCase):
    def test_canonical_files_exist(self) -> None:
        for rel in [
            "SKILL.md",
            "runtime/READ_ONLY_AND_SAFETY.md",
            "runtime/REVIEW_UNIT_AND_CONTEXT.md",
            "runtime/INTAKE_AND_EVIDENCE.md",
            "runtime/COUNCIL_ROUNDS.md",
            "runtime/WRITING_CRAFT_LENS.md",
            "runtime/REVIEW_CHECKLISTS.md",
            "runtime/SCORING_RUBRIC.md",
            "runtime/REPORT_CONTRACT.md",
            "templates/REPORT_TEMPLATE.md",
            "templates/REVIEW_PACKET.md",
            "scripts/check_report.py",
        ]:
            self.assertTrue((SKILL / rel).is_file(), rel)

    def test_release_files(self) -> None:
        for rel in ["LICENSE", "PUBLISH.md", "THIRD_PARTY_NOTICES.md", "VERSION"]:
            self.assertTrue((ROOT / rel).is_file(), rel)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {version}", changelog)

    def test_router_sentinel(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("MANUSCRIPT_REVIEW_ROUTER_EOF: manuscript-review", text)
        self.assertIn("只读", text)
        self.assertIn("只交付报告", text)

    def test_story_craft_lens(self) -> None:
        path = SKILL / "runtime" / "STORY_CRAFT_LENS.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        for term in ["激励事件", "求索", "鸿沟", "幕逆转", "不归点", "人物矛盾", "人物弧", "幕级故事设计分", "序章"]:
            self.assertIn(term, text)
        writing = SKILL / "runtime" / "WRITING_CRAFT_LENS.md"
        self.assertTrue(writing.is_file())
        wtext = writing.read_text(encoding="utf-8")
        for term in ["场景", "对白", "描写", "节奏", "更好的写法", "写作技巧分"]:
            self.assertIn(term, wtext)
        scoring = (SKILL / "runtime" / "SCORING_RUBRIC.md").read_text(encoding="utf-8")
        self.assertIn("写作技巧分（Craft Index）", scoring)
        template = (SKILL / "templates" / "REPORT_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertIn("写作技巧评分（Craft Scorecard）", template)
        self.assertIn("Craft Index", template)

    def test_worldbuilding_removed(self) -> None:
        self.assertFalse((SKILL / "roles" / "worldbuilding.md").exists())
        self.assertFalse((ROOT / ".opencode" / "agents" / "worldbuilding.md").exists())
        self.assertFalse((ROOT / ".claude" / "agents" / "worldbuilding.md").exists())
        self.assertFalse((ROOT / ".codex" / "agents" / "worldbuilding.toml").exists())
        router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("`worldbuilding`", router)

    def test_roles_require_craft_subscores(self) -> None:
        for role in ["story_plot_structure", "character", "scene_dialogue"]:
            text = (SKILL / "roles" / f"{role}.md").read_text(encoding="utf-8")
            self.assertIn("写作技巧", text, role)

    def test_material_handoff_gate(self) -> None:
        router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        intake = (SKILL / "runtime" / "INTAKE_AND_EVIDENCE.md").read_text(encoding="utf-8")
        rounds = (SKILL / "runtime" / "COUNCIL_ROUNDS.md").read_text(encoding="utf-8")
        template = (SKILL / "templates" / "REPORT_TEMPLATE.md").read_text(encoding="utf-8")
        for text in [router, intake]:
            self.assertIn("素材交接门", text)
            self.assertIn("用户确认无", text)
            self.assertIn("未确认", text)
        self.assertIn("不得启动 Round 1", rounds)
        self.assertIn("素材状态", template)

    def test_roles_have_core_sections(self) -> None:
        for role in ROLES:
            path = SKILL / "roles" / f"{role}.md"
            self.assertTrue(path.is_file(), role)
            text = path.read_text(encoding="utf-8")
            for heading in ["角色使命", "输出契约", "边界"]:
                self.assertIn(heading, text, f"{role} missing {heading}")
            self.assertIn(f"Stable Agent ID:** `{role}`", text)

    def test_opencode_adapters(self) -> None:
        for role in ROLES:
            path = ROOT / ".opencode" / "agents" / f"{role}.md"
            self.assertTrue(path.is_file(), role)
            text = path.read_text(encoding="utf-8")
            self.assertIn("mode: subagent", text)
            self.assertIn("edit: deny", text)
            self.assertIn(f"manuscript-review/roles/{role}.md", text)

    def test_claude_adapters(self) -> None:
        for role, cname in CLAUDE_NAMES.items():
            path = ROOT / ".claude" / "agents" / f"{cname}.md"
            self.assertTrue(path.is_file(), cname)
            text = path.read_text(encoding="utf-8")
            self.assertIn("tools: Read, Grep, Glob", text)
            self.assertIn(f"manuscript-review/roles/{role}.md", text)

    def test_codex_adapters(self) -> None:
        for role in ROLES:
            path = ROOT / ".codex" / "agents" / f"{role}.toml"
            self.assertTrue(path.is_file(), role)
            text = path.read_text(encoding="utf-8")
            self.assertIn('sandbox_mode = "read-only"', text)
            self.assertIn(f"manuscript-review/roles/{role}.md", text)

    def test_claude_wrapper(self) -> None:
        path = ROOT / ".claude" / "skills" / "manuscript-review" / "SKILL.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("../../../.agents/skills/manuscript-review/SKILL.md", text)
        self.assertIn("MANUSCRIPT_REVIEW_ROUTER_EOF", text)

    def test_sample_report_passes_lint(self) -> None:
        report = ROOT / "examples" / "sample_report.md"
        script = SKILL / "scripts" / "check_report.py"
        result = subprocess.run(
            [sys.executable, str(script), str(report)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_placeholder_in_sample(self) -> None:
        text = (ROOT / "examples" / "sample_report.md").read_text(encoding="utf-8")
        self.assertNotIn("{{", text)


if __name__ == "__main__":
    unittest.main()
