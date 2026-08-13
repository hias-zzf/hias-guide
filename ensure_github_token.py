#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Best-effort GitHub token bootstrap for builds on any machine.

Tries, in order:
1. environment variables GITHUB_TOKEN / GH_TOKEN
2. ``gh auth token`` (GitHub CLI, for users already logged in with ``gh``)
3. ``git credential fill`` (Git Credential Manager / system keychain)

The first token that passes a lightweight validation is written to
``contributors.local.json`` (git-ignored), which ``revision_hook.py`` already
reads.  Nothing is written if no token can be found; the build then simply
falls back to anonymous GitHub API access.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN_FILE = ROOT / "contributors.local.json"


def _load_existing() -> dict:
    try:
        data = json.loads(TOKEN_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _mask(token: str) -> str:
    return f"{token[:4]}…" if len(token) > 8 else "****"


def _env_token() -> str:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def _gh_token() -> str:
    try:
        proc = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    if proc.returncode == 0:
        return proc.stdout.strip()
    return ""


def _credential_token() -> str:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            env=env,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    creds: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            creds[key.strip()] = value.strip()
    return creds.get("password", "") or creds.get("oauth", "")


def _valid(token: str) -> bool:
    request = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "hias-guide-build",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status == 200
    except urllib.error.HTTPError:
        return False
    except Exception:
        # Network trouble: keep the token rather than discarding it.
        return True


def _write(token: str) -> None:
    data = _load_existing()
    data["github_token"] = token
    TOKEN_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass


def main() -> int:
    existing = _load_existing().get("github_token", "")
    if existing and _valid(existing):
        print(f"[token] contributors.local.json 中已有 Token：{_mask(existing)}")
        return 0
    if existing:
        print("[token] contributors.local.json 中的 Token 已失效，尝试重新获取。")

    sources = (
        ("环境变量 GITHUB_TOKEN/GH_TOKEN", _env_token()),
        ("gh auth token", _gh_token()),
        ("git credential fill", _credential_token()),
    )
    for label, token in sources:
        if not token:
            continue
        if not _valid(token):
            print(f"[token] {label} 返回的 Token 无效，跳过。")
            continue
        print(f"[token] 从 {label} 获取成功：{_mask(token)}")
        _write(token)
        print("[token] 已写入 contributors.local.json（该文件已被 git 忽略）")
        return 0

    if existing:
        try:
            TOKEN_FILE.unlink()
        except OSError:
            pass
    print("[token] 未找到可用 Token，构建将使用匿名 GitHub API（60 次/小时）。")
    print("[token] 提示：可运行 `gh auth login` 登录，或手动创建 contributors.local.json。")
    return 0


if __name__ == "__main__":
    sys.exit(main())