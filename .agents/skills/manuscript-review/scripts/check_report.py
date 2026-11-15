#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正文审核报告结构检查器（只读）。

用法：
    python3 check_report.py <report.md>

只读取报告文件，不写入任何内容。用于检查已保存的报告是否包含
必需章节、只读声明、评分范围、P0 证据锚点与明显占位符。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "审核摘要",
    "审核范围与依据",
    "章节速写",
    "分维度评价",
    "关键问题清单",
    "修改方案",
    "圆桌争议",
    "亮点与保留项",
    "评分明细",
    "覆盖范围",
]

DIMENSIONS = ["场景与戏剧效果", "对白与人物声音", "描写与文字", "节奏与可读性", "人物与情感", "幕/序列效果"]

FORBIDDEN_PHRASES = [
    "已修改用户文件",
    "已替换原文件",
    "已保存原稿",
    "文件已更新",
    "已删除原文件",
]


def section(text: str, title: str) -> str:
    """Return the body of an H2 section, excluding nested H3 splits."""
    pattern = re.compile(rf"^##\s+(?:\d+\.\s*)?{re.escape(title)}.*?$(.*?)(?=^##\s+|\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group(1) if match else ""


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python3 check_report.py <report.md>")
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"[错误] 找不到报告文件: {path}")
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    warnings: list[str] = []

    # 1. 必需章节
    missing = [s for s in REQUIRED_SECTIONS if not re.search(rf"^##\s+(?:\d+\.\s*)?{re.escape(s)}", text, re.M)]
    if missing:
        errors.append("缺少必需章节: " + "；".join(missing))

    # 2. 占位符
    if "{{" in text or "}}" in text:
        errors.append("报告仍包含未替换的模板占位符 {{...}}")

    # 3. 只读声明
    if "只读声明" not in text:
        errors.append("缺少“只读声明”")
    elif "未对任何用户提供的输入文件执行写入" not in text and "未对任何用户文件执行写入" not in text and "未调用任何写入操作" not in text:
        warnings.append("只读声明存在，但未明确写出“未对任何用户提供的输入文件执行写入/未调用任何写入操作”")

    # 4. 虚假写入声明
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            errors.append(f"出现疑似虚假写入声明: “{phrase}”")

    # 5. 总分范围
    score_match = re.search(r"总分\*{0,2}\s*[：:]\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10", text)
    total: float | None = None
    if not score_match:
        warnings.append("未解析到“总分：x.x / 10”")
    else:
        total = float(score_match.group(1))
        if not 0 <= total <= 10:
            errors.append(f"总分超出 0–10 范围: {total}")

    # 6. 维度表
    for dim in DIMENSIONS:
        if dim not in text:
            warnings.append(f"未找到维度: {dim}")

    # 7. 评分明细权重（六维 / 单章重分配）
    weight_groups = [("25%", "27.8%"), ("20%", "22.2%"), ("15%", "16.7%"), ("10%", "11.1%")]
    for group in weight_groups:
        if not any(w in text for w in group):
            warnings.append(f"评分明细中未找到权重 {' 或 '.join(group)}")

    # 7.1 写作技巧 / 故事设计评分（Craft）
    if "写作技巧评分（Craft Scorecard）" in text:
        craft_items = ["场景目标/转折", "对白行动/潜台词", "人物声音", "描写/感官/POV", "节奏/句法", "情绪落点", "人物欲望/矛盾", "人物弧/关系", "幕/序列升级/逆转", "类型契约/读者体验"]
        missing_craft = [x for x in craft_items if x not in text]
        if missing_craft:
            warnings.append("写作技巧 Scorecard 缺少项目: " + "、".join(missing_craft))
    elif "故事设计评分（Craft Scorecard）" in text:
        craft_items = ["激励事件", "求索", "鸿沟", "场景价值转折", "不归点", "人物矛盾", "人物弧"]
        missing_craft = [x for x in craft_items if x not in text]
        if missing_craft:
            warnings.append("故事设计 Scorecard 缺少项目: " + "、".join(missing_craft))
    else:
        warnings.append("缺少“写作技巧评分（Craft Scorecard）”或“故事设计评分（Craft Scorecard）”")
    if "Craft Index" not in text and "写作技巧分" not in text:
        warnings.append("缺少“写作技巧分（Craft Index）”")
    if "审核单位" not in text:
        warnings.append("缺少“审核单位”（单章/序列/幕/卷）")

    # 8. P0 证据锚点
    modify = section(text, "修改方案")
    p0_part = re.split(r"^###\s+P1", modify, maxsplit=1, flags=re.M)[0]
    if "P0" in p0_part and "必须处理" in p0_part:
        has_p0_content = bool(re.search(r"####\s+", p0_part))
        if has_p0_content and not re.search(r"\[(正文|素材|缺口|推断)·", p0_part):
            errors.append("P0 修改方案缺少正文/素材证据锚点（[正文·…] / [素材·…]）")

    # 9. P0 数量与总分上限（只警告，因为“未解决”需人工判断）
    problems = section(text, "关键问题清单")
    p0_count = len(re.findall(r"\|\s*\**P0\**\s*\|", problems))
    if p0_count and total is not None:
        cap = 6.5 if p0_count == 1 else (5.8 if p0_count == 2 else 5.0)
        if total > cap + 0.01:
            warnings.append(
                f"清单中有 {p0_count} 条 P0，按规则总分上限应为 {cap}，当前总分为 {total}；"
                "若 P0 已解决/撤回请在报告中说明"
            )

    # 10. 引文长度粗检（>60 字的引文可能过度复制）
    long_quotes = [q for q in re.findall(r'“([^”]{61,})”', text)]
    if long_quotes:
        warnings.append(f"发现 {len(long_quotes)} 处超过 60 字的引文，建议压缩到定位所需长度")

    print(f"检查文件: {path}")
    print(f"字数: {len(text)}")
    if errors:
        print(f"\n错误 ({len(errors)}):")
        for item in errors:
            print(f"  ✗ {item}")
    if warnings:
        print(f"\n提醒 ({len(warnings)}):")
        for item in warnings:
            print(f"  ! {item}")
    if not errors and not warnings:
        print("\n✓ 结构检查通过")
    elif not errors:
        print("\n✓ 无结构性错误（有提醒）")
    else:
        print("\n✗ 存在结构性错误")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
