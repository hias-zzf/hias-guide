#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inject auto-generated experience cards into the built homepage / 简介 landing."""

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


def main(homepage: Path, experiences_dir: Path) -> None:
    html = homepage.read_text(encoding="utf-8")
    marker = '<div class="isc-exp-grid" id="experience-cards">'
    if marker not in html:
        return

    # 卡片链接相对于目标页面所在目录，保证首页与 简介/ 均可复用
    prefix = os.path.relpath(experiences_dir, homepage.parent).replace("\\", "/")
    cards = []
    if experiences_dir.exists():
        for md in sorted(experiences_dir.glob("*.md")):
            if md.name in ("README.md", "index.md"):
                continue
            cards.append(card_for(md, prefix))

    if cards:
        body = "\n".join(cards)
        html = re.sub(
            r'<div class="isc-exp-grid" id="experience-cards">.*?</div>\s*</div>',
            '<div class="isc-exp-grid" id="experience-cards">\n' + body + "\n</div>",
            html,
            flags=re.S,
        )
    homepage.write_text(html, encoding="utf-8")
    print(f"经验卡片已更新，共 {len(cards)} 篇。")
    return prefix


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
