param(
    [switch]$Serve
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (python -c "import material" 2>$null)) {
    python -m pip install -r requirements.txt
}

python update_nav.py

if (Test-Path -LiteralPath "docs_src") {
    Remove-Item -LiteralPath "docs_src" -Recurse -Force
}
New-Item -ItemType Directory -Path "docs_src" | Out-Null

Copy-Item -LiteralPath "初试准备", "复试准备", "上岸经验分享" -Destination "docs_src" -Recurse
Copy-Item -LiteralPath "经验分享投稿模板.md", "CONTRIBUTORS.md", "免责声明.md" -Destination "docs_src"

python anonymize.py docs_src
Copy-Item -LiteralPath "homepage.md" -Destination "docs_src\index.md"
python update_homepage.py docs_src\index.md docs_src\上岸经验分享

python -m mkdocs build

if ($Serve) {
    python -m mkdocs serve
}

