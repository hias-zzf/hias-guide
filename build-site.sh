#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! python -c "import material" 2>/dev/null; then
  python -m pip install -r requirements.txt
fi

python update_nav.py

rm -rf docs_src
mkdir -p docs_src

# 内容目录：简介（合并首页）+ 各学院栏目
for dir in 简介 智能学院 物理与光电工程学院 其它学院; do
  if [ -d "$dir" ]; then
    cp -r "$dir" docs_src/
  fi
done

python anonymize.py docs_src
cp homepage.md docs_src/index.md
python update_homepage.py docs_src/index.md "docs_src/智能学院/上岸经验分享"
python update_homepage.py "docs_src/简介/index.md" "docs_src/智能学院/上岸经验分享"

python -m mkdocs build
echo "构建完成：$(pwd)/site/index.html"