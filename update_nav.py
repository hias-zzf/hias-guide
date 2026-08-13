#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scan content folders and regenerate the nav section of mkdocs.yml.

The nav section is replaced *textually* so the rest of mkdocs.yml
(including `!!python/name:` tags used by pymdown extensions) is preserved.

Layout:
  * 简介          -> merged 首页 + 简介（杭高院整体介绍 + 报考指南）
  * 智能学院       -> 整体介绍 / 085404 / 085410 / 085408
  * 物理与光电工程学院 -> 整体介绍 / 085410人工智能（02 小卫星联培 · 03 智能光电）
  * 其它学院       -> 待拓展

To control page order inside a folder, add an entry to NAV_ORDER below;
items not listed are appended in alphabetical order.
"""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent

# 顶层栏目顺序
SECTIONS = ["简介", "智能学院", "物理与光电工程学院", "其它学院"]

# 各栏目内部顺序（未列出的项按字母序排在后面）
NAV_ORDER: dict[str, list[str]] = {
    "简介": [
        "index.md",
        "培养与生活.md",
        "补助与费用.md",
        "经验分享投稿模板.md",
        "CONTRIBUTORS.md",
        "免责声明.md",
    ],
    "智能学院": [
        "整体介绍.md",
        "招生专业",
        "初试准备",
        "复试准备",
        "上岸经验分享",
    ],
    "智能学院/招生专业": ["index.md", "085404计算机技术.md", "085410人工智能.md", "085408光电信息工程.md"],
    "物理与光电工程学院": ["整体介绍.md", "招生专业", "拟录取信息"],
    "物理与光电工程学院/拟录取信息": ["整体趋势", "25年拟录取信息", "26年拟录取信息"],
}


def entries_for(folder: Path, prefix: str) -> list[dict]:
    # 按文件夹完整路径（如 "智能学院/招生专业"）查 NAV_ORDER
    order = NAV_ORDER.get(prefix.rstrip("/"))
    names = [p.name for p in folder.iterdir()]
    if order:
        ordered = [n for n in order if n in names]
        rest = sorted((n for n in names if n not in order), key=lambda s: (s != "index.md", s.lower()))
        names = ordered + rest
    else:
        names = sorted(names, key=lambda s: (s != "index.md", s.lower()))

    entries: list[dict] = []
    for name in names:
        item = folder / name
        rel = (prefix + name).replace("\\", "/")
        if item.is_dir():
            children = entries_for(item, rel + "/")
            if children:
                # 目录下只有同名 index.md 时，直接作为单页展示（避免双重嵌套）
                if len(children) == 1 and list(children[0].keys()) == [name]:
                    entries.append({name: children[0][name]})
                else:
                    entries.append({name: children})
        elif item.suffix == ".md" and item.name != "README.md":
            if item.name == "index.md":
                label = prefix.rstrip("/").split("/")[-1] or name
                entries.append({label: rel})
            else:
                entries.append({item.stem: rel})
    return entries


def build_nav() -> list[dict]:
    nav: list[dict] = []
    for sec in SECTIONS:
        folder = ROOT / sec
        if not folder.exists():
            continue
        entries = entries_for(folder, sec + "/")
        if not entries:
            continue
        # 栏目下只有 index.md 时，直接作为页面（如 其它学院）
        if len(entries) == 1 and list(entries[0].keys()) == [sec]:
            nav.append({sec: entries[0][sec]})
        else:
            nav.append({sec: entries})
    return nav


def replace_nav_section(text: str, nav: list[dict]) -> str:
    lines = text.splitlines()
    nav_idx = None
    next_idx = len(lines)
    for i, line in enumerate(lines):
        if nav_idx is None and re.match(r"^nav\s*:", line):
            nav_idx = i
            continue
        if nav_idx is not None and i > nav_idx and re.match(r"^[A-Za-z_][\w]*\s*:", line):
            next_idx = i
            break
    nav_yaml = yaml.dump(nav, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    if nav_idx is None:
        return text.rstrip() + "\n\nnav:\n" + nav_yaml + "\n"
    head = "\n".join(lines[:nav_idx])
    tail = "\n".join(lines[next_idx:]) if next_idx < len(lines) else ""
    block = "nav:\n" + nav_yaml
    if tail:
        return head.rstrip() + "\n" + block + "\n" + tail
    return head.rstrip() + "\n" + block + "\n"


def main() -> None:
    config_path = ROOT / "mkdocs.yml"
    text = config_path.read_text(encoding="utf-8")
    nav = build_nav()
    new_text = replace_nav_section(text, nav)
    config_path.write_text(new_text, encoding="utf-8")
    print(f"导航已生成，共 {len(nav)} 个顶层栏目。")


if __name__ == "__main__":
    main()