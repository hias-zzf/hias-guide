#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Cloudflare Pages 默认浅克隆，先补全 Git 历史才能算出完整贡献者列表
if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
  echo "检测到浅克隆，拉取完整 Git 历史..."
  git fetch --unshallow
fi

# 自动获取/复用已登录用户的 GitHub Token，写入 contributors.local.json
python ensure_github_token.py

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
python update_homepage.py docs_src/index.md "docs_src/智能学院/上岸经验分享" --limit 6
python update_homepage.py "docs_src/简介/index.md" "docs_src/智能学院/上岸经验分享" --limit 6
python update_homepage.py "docs_src/智能学院/上岸经验分享/index.md" "docs_src/智能学院/上岸经验分享"

python -m mkdocs build
echo "构建完成：$(pwd)/site/index.html"
