# 国科大杭高智能学院考研报考指南

非官方公益报考指南，内容依据《杭高智能报考指南 V1.4.0（2026/5/9）》整理。

## 目录结构

```text
.
├─ homepage.md                 # 首页精装落地页
├─ 初试准备/                   # 初试相关资料，放 .md 即可
├─ 复试准备/                   # 复试、培养、导师相关资料
├─ 上岸经验分享/               # 经验贴，直接放 .md 文件
├─ 经验分享投稿模板.md
├─ CONTRIBUTORS.md
├─ 免责声明.md
├─ overrides/                  # 首页样式与模板覆盖
├─ build-site.ps1 / .sh        # 构建脚本
└─ update_nav.py               # 自动扫描内容并生成导航
```

## 怎么用

1. 把资料放进对应文件夹：
   - 初试信息放 `初试准备/`
   - 复试、培养、导师信息放 `复试准备/`
   - 经验贴放 `上岸经验分享/`，一个经验贴一个 `.md` 文件
2. 运行构建脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\build-site.ps1
```

```bash
bash build-site.sh
```

3. 本地预览：

```powershell
python -m mkdocs serve
```

打开 <http://127.0.0.1:8000/>。

脚本会自动扫描 `初试准备/`、`复试准备/`、`上岸经验分享/` 下的 Markdown 文件并生成导航，所以新增内容后不需要手动改 `mkdocs.yml`，直接放文件再重新构建即可。

首页的“经验分享”卡片也会由 `update_homepage.py` 在构建时自动生成，标题取文件名，摘要取正文第一段。

## 经验贴格式

参考 [经验分享投稿模板.md](经验分享投稿模板.md)。想匿名展示学校时，把学校名加入 `anonymize.py` 的 `REPLACEMENTS`，构建时会在 `docs_src/` 副本中自动替换，仓库源文件不受影响。

## 部署

构建产物在 `site/`，可直接部署到 GitHub Pages、Cloudflare Pages 等静态托管。
