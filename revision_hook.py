#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MkDocs hook: compute per-page footer metadata.

Populates ``page.meta`` with:
- ``footer_revision_date``:  last commit time (fixed UTC+8)
- ``footer_history_url``:    GitHub commit-history URL
- ``footer_edit_url``:       GitHub edit URL
- ``footer_contributors``:   ``[{"name": ..., "url": ...}, ...]``

Resolution strategy for contributor links:

1. Local ``git log`` lists the authors of each file (fast, no API call per
   page).
2. GitHub noreply e-mails directly yield the username.
3. ``contributors.json`` manual overrides map a name/e-mail to a canonical
   GitHub username (used offline as well).
4. One global commits API call maps linked e-mails/names to ``author.login``.
5. Unlinked authors are checked against ``https://github.com/<name>`` with an
   exact-match requirement, falling back to the search API if the core API is
   rate-limited.

Authors that resolve to no GitHub username are skipped, and a warning is
printed to the build console instead of listing the raw Git name.

No e-mail address is stored in this repository.

This project builds from ``docs_src/``, a generated copy that is listed in
``.gitignore``.  The stock ``mkdocs-git-revision-date-localized-plugin`` would
therefore only see the build time, because ``git log`` cannot find history for
generated files.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
TIMEZONE = timezone(timedelta(hours=8))

# ``docs_src`` mirrors the top-level content folders.  The homepage is the only
# exception: ``homepage.md`` is copied to ``docs_src/index.md``.
SRC_MAP = {
    "index.md": "homepage.md",
}

# Configuration is loaded from ``contributors.json``.  A local override file
# ``contributors.local.json`` (git-ignored) is read first and may override it.
# The special ``github_token`` key is never treated as a contributor link.
def _load_config() -> tuple[dict[str, str], str]:
    links: dict[str, str] = {}
    token = ""
    for filename in ("contributors.local.json", "contributors.json"):
        try:
            data = json.loads((ROOT / filename).read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for key, value in data.items():
            if key.lower() == "github_token":
                if isinstance(value, str) and value and not token:
                    token = value
                continue
            if isinstance(value, str) and value:
                links[str(key).lower()] = value
    return links, token


CONTRIBUTOR_LINKS, FILE_TOKEN = _load_config()

_GITHUB_NOREPLY_RE = re.compile(
    r"^(?:\d+\+)?(?P<user>[^@]+)@users\.noreply\.github\.com$",
    re.IGNORECASE,
)

# State for the one global commits API request per build run.
_REMOTE_FETCHED = False
_REMOTE_AUTHOR_MAP: dict[str, str] = {}

# Caches name -> login lookups during one build run.
_USERNAME_CACHE: dict[str, str | None] = {}


def _source_path(src_path: str) -> str:
    """Map a generated docs_src path back to a repo-relative tracked path."""
    src_path = src_path.replace("\\", "/")
    return SRC_MAP.get(src_path, src_path)


def _branch(config) -> str:
    """Extract the branch name from Material's ``edit_uri``."""
    edit_uri = (getattr(config, "edit_uri", "") or "")
    if not edit_uri:
        return "main"
    parts = [p for p in edit_uri.strip("/").split("/") if p]
    return parts[-1] if parts else "main"


def _repo_url(config) -> str:
    return (getattr(config, "repo_url", "") or "").rstrip("/")


def _github_owner_repo(repo_url: str):
    """Return ``(owner, repo)`` for a GitHub repository URL, or ``None``."""
    if not repo_url:
        return None
    repo_url = repo_url.rstrip("/")
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    marker = "github.com/"
    pos = repo_url.find(marker)
    if pos < 0:
        return None
    parts = repo_url[pos + len(marker):].split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None


def _api_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hias-guide-build",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or FILE_TOKEN
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_json(url: str):
    request = urllib.request.Request(url, headers=_api_headers())
    with urllib.request.urlopen(request, timeout=6) as response:
        return json.load(response)


def _run_git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.stdout if proc.returncode == 0 else ""


def _last_commit_timestamp(repo_path: str) -> int | None:
    value = _run_git(["log", "-1", "--format=%at", "--", repo_path]).strip()
    return int(value) if value.isdigit() else None


def _github_username(email: str) -> str | None:
    """Extract the GitHub username from a GitHub noreply commit e-mail."""
    match = _GITHUB_NOREPLY_RE.match(email)
    return match.group("user") if match else None


def _build_remote_author_map(owner: str, repo: str, branch: str) -> dict[str, str]:
    """Fetch linked author names/e-mails once for the whole build run."""
    global _REMOTE_FETCHED, _REMOTE_AUTHOR_MAP
    if _REMOTE_FETCHED:
        return _REMOTE_AUTHOR_MAP
    _REMOTE_FETCHED = True

    url = (
        f"https://api.github.com/repos/{owner}/{repo}/commits"
        f"?sha={quote(branch, safe='')}&per_page=100"
    )
    try:
        data = _fetch_json(url)
    except Exception:
        return _REMOTE_AUTHOR_MAP

    for item in data:
        if not isinstance(item, dict):
            continue
        login = (item.get("author") or {}).get("login")
        if not login:
            continue
        commit_author = (item.get("commit") or {}).get("author") or {}
        name = commit_author.get("name") or ""
        email = commit_author.get("email") or ""
        if name:
            _REMOTE_AUTHOR_MAP[name.lower()] = login
        if email:
            _REMOTE_AUTHOR_MAP[email.lower()] = login
    return _REMOTE_AUTHOR_MAP


def _github_profile_login(name: str) -> str | None:
    """Resolve an author name to a login only on an exact profile match."""
    key = name.lower()
    if key in _USERNAME_CACHE:
        return _USERNAME_CACHE[key]
    if not name:
        _USERNAME_CACHE[key] = None
        return None

    login = None
    try:
        data = _fetch_json(f"https://api.github.com/users/{quote(name, safe='')}")
        if isinstance(data, dict):
            candidate = data.get("login")
            if candidate and candidate.lower() == key:
                login = candidate
    except Exception:
        login = None

    if login is None:
        try:
            data = _fetch_json(
                "https://api.github.com/search/users"
                f"?q=login%3A{quote(name, safe='')}&per_page=5"
            )
            for item in (data.get("items") or []) if isinstance(data, dict) else []:
                candidate = item.get("login")
                if candidate and candidate.lower() == key:
                    login = candidate
                    break
        except Exception:
            login = None

    _USERNAME_CACHE[key] = login
    return login


def _local_authors(repo_path: str) -> list[tuple[str, str]]:
    """Return ``(name, email)`` authors for a file, newest first."""
    log = _run_git(["log", "--follow", "--format=%an|%ae", "--", repo_path])
    authors: list[tuple[str, str]] = []
    for line in log.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            name, email = line.split("|", 1)
        else:
            name, email = line, ""
        authors.append((name, email))
    return authors


def _apply_contributor_links(contributors: list[dict]) -> list[dict]:
    """Attach profile URLs from ``CONTRIBUTOR_LINKS`` where missing."""
    for entry in contributors:
        if not entry.get("url"):
            entry["url"] = CONTRIBUTOR_LINKS.get(entry.get("name", "").lower(), "")
    return contributors


def _github_username_from_url(url: str) -> str | None:
    """Extract a GitHub login from a ``https://github.com/<login>`` URL."""
    if not url:
        return None
    marker = "github.com/"
    pos = url.find(marker)
    if pos < 0:
        return None
    login = url[pos + len(marker):].strip("/").split("/")[0]
    return login or None


def _link_username(name: str, email: str) -> str | None:
    """Resolve a canonical GitHub username from ``contributors.json`` links."""
    for key in (name.lower(), email.lower()):
        login = _github_username_from_url(CONTRIBUTOR_LINKS.get(key, ""))
        if login:
            return login
    return None


def _contributors(repo_path: str, repo_url: str, branch: str) -> list[dict]:
    """Return unique contributors, newest first.

    Authors that cannot be resolved to a GitHub username are skipped with a
    warning on the build console instead of being listed under a raw name.
    """
    owner_repo = _github_owner_repo(repo_url)
    remote_map = (
        _build_remote_author_map(owner_repo[0], owner_repo[1], branch)
        if owner_repo
        else {}
    )

    seen: set[str] = set()
    warned: set[str] = set()
    result: list[dict] = []
    for name, email in _local_authors(repo_path):
        username = _github_username(email)
        if not username:
            username = _link_username(name, email)
        if not username and email and email.lower() in remote_map:
            username = remote_map[email.lower()]
        if not username and name.lower() in remote_map:
            username = remote_map[name.lower()]
        if not username:
            username = _github_profile_login(name)

        if not username:
            warn_key = f"{name}|{email}"
            if warn_key not in warned:
                warned.add(warn_key)
                print(
                    f"[revision_hook] WARNING: cannot resolve a GitHub username "
                    f"for author {name!r} <{email}>; this contributor is "
                    f"skipped. Add a mapping in contributors.json to include "
                    f"them.",
                    file=sys.stderr,
                )
            continue

        key = username.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "name": username,
                "url": f"https://github.com/{username}",
            }
        )
    return _apply_contributor_links(result)


def on_page_context(context, *, page, config, nav):
    """Populate ``page.meta`` with revision date and footer URLs."""
    src_path = getattr(page.file, "src_path", None)
    if not src_path:
        return context

    repo_path = _source_path(src_path)
    timestamp = _last_commit_timestamp(repo_path)
    if timestamp is None:
        timestamp = int(datetime.now(TIMEZONE).timestamp())

    dt = datetime.fromtimestamp(timestamp, TIMEZONE)
    formatted = (
        f"{dt.year}/{dt.month}/{dt.day} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    )

    repo_url = _repo_url(config)
    branch = _branch(config)

    history_url = ""
    edit_url = ""
    if repo_url:
        encoded = quote(repo_path, safe="/")
        history_url = f"{repo_url}/commits/{branch}/{encoded}"
        edit_url = f"{repo_url}/edit/{branch}/{encoded}"

    meta = getattr(page, "meta", None)
    if meta is None:
        meta = {}
        page.meta = meta
    meta["footer_revision_date"] = formatted
    meta["footer_history_url"] = history_url
    meta["footer_edit_url"] = edit_url
    meta["footer_contributors"] = _contributors(repo_path, repo_url, branch)

    return context