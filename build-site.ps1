param(
    [switch]$Serve
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 自动获取/复用已登录用户的 GitHub Token，写入 contributors.local.json
python ensure_github_token.py

if (-not (python -c "import material" 2>$null)) {
    python -m pip install -r requirements.txt
}

python update_nav.py

if (Test-Path -LiteralPath "docs_src") {
    Remove-Item -LiteralPath "docs_src" -Recurse -Force
}
New-Item -ItemType Directory -Path "docs_src" | Out-Null

# 内容目录：简介（合并首页）+ 各学院栏目
$ContentDirs = @("简介", "智能学院", "物理与光电工程学院", "其它学院")
foreach ($dir in $ContentDirs) {
    if (Test-Path -LiteralPath $dir) {
        Copy-Item -LiteralPath $dir -Destination "docs_src" -Recurse
    }
}

python anonymize.py docs_src
Copy-Item -LiteralPath "homepage.md" -Destination "docs_src\index.md"
python update_homepage.py docs_src\index.md docs_src\智能学院\上岸经验分享 --limit 6
python update_homepage.py docs_src\简介\index.md docs_src\智能学院\上岸经验分享 --limit 6
python update_homepage.py docs_src\智能学院\上岸经验分享\index.md docs_src\智能学院\上岸经验分享

python -m mkdocs build

if ($Serve) {
    python -m mkdocs serve
}