#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optional build-time anonymization for experience posts.

Replaces exact school names with a generic level (985 / 双非 / 四非 etc.)
inside docs_src only. Source files in the repository stay untouched.

To use it, add rules below, e.g.:
    ("杭州电子科技大学", "双非"),
"""

import re
import sys
from pathlib import Path


REPLACEMENTS: list[tuple[str, str]] = []
DROP_SECTIONS = ["## 联系方式"]
# 仅对经验贴生效：删除「## 联系方式」之后的内容，避免公开个人联系方式
DROP_SECTIONS_ONLY_IN = "上岸经验分享"

_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def protect_links(text: str) -> tuple[str, dict[str, str]]:
    placeholder: dict[str, str] = {}
    counter = 0

    def _repl(m: re.Match) -> str:
        nonlocal counter
        key = f"\x00LINK{counter}\x00"
        placeholder[key] = m.group(2)
        counter += 1
        return f"[{m.group(1)}]({key})"

    return _LINK_RE.sub(_repl, text), placeholder


def restore_links(text: str, placeholder: dict[str, str]) -> str:
    for key, url in placeholder.items():
        text = text.replace(key, url)
    return text


def main(docs_dir: str) -> None:
    root = Path(docs_dir)
    if not root.is_dir():
        sys.exit(f"目录不存在: {docs_dir}")
    changed = 0
    for md in sorted(root.rglob("*.md")):
        original = md.read_text(encoding="utf-8")
        text, placeholder = protect_links(original)
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        # 「## 联系方式」删除逻辑仅作用于经验贴，避免误删结构化页面的官方联系方式
        if DROP_SECTIONS_ONLY_IN in md.as_posix():
            for section in DROP_SECTIONS:
                if section in text:
                    text = text.split(section)[0].rstrip() + "\n"
        text = restore_links(text, placeholder)
        if text != original:
            md.write_text(text, encoding="utf-8")
            print(f"  [anonymize] 已处理 {md.relative_to(root)}")
            changed += 1
    print(f"匿名化完成，共处理 {changed} 个文件。")


if __name__ == "__main__":
    main(sys.argv[1])
