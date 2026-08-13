#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inject auto-generated experience cards into the built homepage / 简介 landing.

Usage:
    python update_homepage.py <homepage.md> <experiences_dir> [--limit N]
"""

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote


KEYWORD_TAGS = ("双非", "跨考", "二战", "三无", "二本", "科班", "弱基础", "985", "211")


def card_for(md_file: Path, prefix: str) -> str:
    text = md_file.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = md_file.stem
    tag = next((kw for kw in KEYWORD_TAGS if kw in title), "经验")
    summary = ""
    for line in lines[1:]:
        cleaned = re.sub(r"^#{1,6}\s*", "", line)
        cleaned = re.sub(r"^[-•▪]\s*", "", cleaned)
        if cleaned and not re.fullmatch(r"\d{1,4}", cleaned):
            summary = cleaned
            break
    summary = summary[:64] + ("..." if len(summary) > 64 else "")
    href = f"{prefix}/{quote(md_file.stem)}/"
    return (
        '<a class="isc-exp-card" href="' + href + '">'
        '<span class="isc-tag">' + tag + "</span>"
        '<span class="isc-exp-card__title">' + title + "</span>"
        "<p>" + summary + "</p>"
        "</a>"
    )


def more_card(prefix: str) -> str:
    return (
        '<a class="isc-exp-card isc-exp-card--more" href="' + prefix + '/">'
        '<span class="isc-tag">更多</span>'
        '<span class="isc-exp-card__title">更多经验…</span>'
        "<p>查看全部上岸经验分享</p>"
        "</a>"
    )


def main(homepage: Path, experiences_dir: Path, limit: int | None = None) -> str:
    html = homepage.read_text(encoding="utf-8")
    marker = '<div class="isc-exp-grid" id="experience-cards">'
    if marker not in html:
        return ""

    # 卡片链接相对于目标页面所在目录，保证首页与 简介/ 均可复用
    prefix = os.path.relpath(experiences_dir, homepage.parent).replace("\\", "/")
    cards = []
    if experiences_dir.exists():
        for md in sorted(experiences_dir.glob("*.md")):
            if md.name in ("README.md", "index.md"):
                continue
            cards.append(card_for(md, prefix))

    total = len(cards)
    if limit is not None and total > limit:
        cards = cards[:limit]
        cards.append(more_card(prefix))

    if cards:
        body = "\n".join(cards)
        html = re.sub(
            r'<div class="isc-exp-grid" id="experience-cards">.*?</div>\s*</div>',
            '<div class="isc-exp-grid" id="experience-cards">\n' + body + "\n</div>",
            html,
            flags=re.S,
        )
    homepage.write_text(html, encoding="utf-8")
    shown = f"{len(cards)} 篇" + (f"（共 {total} 篇）" if limit is not None else "")
    print(f"经验卡片已更新：{shown}。")
    return prefix


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("homepage")
    parser.add_argument("experiences_dir")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    main(Path(args.homepage), Path(args.experiences_dir), args.limit)