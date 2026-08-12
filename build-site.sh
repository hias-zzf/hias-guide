#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! python -c "import material" 2>/dev/null; then
  python -m pip install -r requirements.txt
fi

python update_nav.py

rm -rf docs_src
mkdir -p docs_src
cp -r 初试准备 复试准备 上岸经验分享 docs_src/
cp 经验分享投稿模板.md CONTRIBUTORS.md 免责声明.md docs_src/

python anonymize.py docs_src
cp homepage.md docs_src/index.md
python update_homepage.py docs_src/index.md docs_src/上岸经验分享

python -m mkdocs build
echo "构建完成：$(pwd)/site/index.html"
