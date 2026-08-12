#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scan content folders and regenerate the nav section of mkdocs.yml."""

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
CONTENT_FOLDERS = ["初试准备", "复试准备", "上岸经验分享"]


def entries_for(folder: Path, prefix: str = "") -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in sorted(folder.iterdir(), key=lambda p: p.name):
        rel = (prefix + item.name).replace("\\", "/")
        if item.is_dir():
            children = entries_for(item, rel + "/")
            if children:
                entries.append({item.name: children})
        elif item.suffix == ".md" and item.name != "README.md":
            entries.append({item.stem: rel})
    return entries


def main() -> None:
    config_path = ROOT / "mkdocs.yml"
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    nav: list[dict[str, Any]] = [{"首页": "index.md"}]
    for folder_name in CONTENT_FOLDERS:
        folder = ROOT / folder_name
        if not folder.exists():
            continue
        entries = entries_for(folder, folder_name + "/")
        if entries:
            nav.append({folder_name: entries})

    nav.extend(
        [
            {"投稿模板": "经验分享投稿模板.md"},
            {"贡献者名单": "CONTRIBUTORS.md"},
            {"免责声明": "免责声明.md"},
        ]
    )
    config["nav"] = nav

    with config_path.open("w", encoding="utf-8") as fh:
        yaml.dump(config, fh, allow_unicode=True, sort_keys=False, width=1000)

    print(f"导航已生成，共 {len(nav)} 个顶层栏目。")


if __name__ == "__main__":
    main()
