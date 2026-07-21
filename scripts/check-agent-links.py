#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Link-check the agent-facing markdown that Sphinx's linkcheck does not cover.

Sphinx's `linkcheck` builder only sees files in the `docs/` build. The
agent-facing files -- `AGENTS.md`, `CLAUDE.md`, `README.md`, `AUTHORING.md`,
`skills/**`, `.cursor/**` -- are consumed as plain markdown and can drift to
dead URLs with no signal (see AUTHORING.md, "Validating links").

This fills that gap with the standard library only. Its philosophy mirrors the
Sphinx linkcheck CI job: non-blocking (run as `allow_failure`), and
*conservative* -- it fails only on definitively dead links (HTTP 404 / 410).
Timeouts, 403s, 5xx, and connection resets are reported as warnings, not
failures, since those are usually flaky hosts or anti-bot responses rather than
broken links. Redirects that resolve are fine here (unlike the stricter docs
linkcheck) -- the bar for agent files is "reachable".
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Agent-facing files Sphinx does not build.
TARGET_GLOBS = [
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "AUTHORING.md",
    "skills/**/*.md",
    ".cursor/rules/*.mdc",
]

URL_RE = re.compile(r"https?://[^\s)\]<>\"'`]+")
TRAILING = ".,;:!?"  # trailing punctuation that is not part of the URL
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
TIMEOUT = 20
DEAD_CODES = {404, 410}


def find_urls() -> dict[str, list[str]]:
    """Return {url: [files it appears in]} across the target files."""
    found: dict[str, set[str]] = {}
    for pattern in TARGET_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if not path.is_file():
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            for raw in URL_RE.findall(path.read_text(encoding="utf-8")):
                found.setdefault(raw.rstrip(TRAILING), set()).add(rel)
    return {u: sorted(f) for u, f in sorted(found.items())}


def check(url: str) -> tuple[str, str]:
    """Return (verdict, detail); verdict in {'ok', 'dead', 'warn'}."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return "ok", str(resp.status)
        except urllib.error.HTTPError as exc:
            if exc.code in DEAD_CODES:
                return "dead", f"HTTP {exc.code}"
            if exc.code == 405 and method == "HEAD":
                continue  # method not allowed -> retry with GET
            return "warn", f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001 - network errors are warnings, not failures
            if method == "GET":
                return "warn", type(exc).__name__
            continue  # socket-level HEAD failure -> retry with GET
    return "warn", "unreachable"


def main() -> int:
    urls = find_urls()
    lines = [f"Checking {len(urls)} unique link(s) across agent-facing files...", ""]
    dead, warn = [], []
    for url, files in urls.items():
        verdict, detail = check(url)
        if verdict == "dead":
            dead.append(f"DEAD  {url}  ({detail})  in {', '.join(files)}")
        elif verdict == "warn":
            warn.append(f"warn  {url}  ({detail})  in {', '.join(files)}")
    if warn:
        lines.append("Warnings (flaky / anti-bot / unreachable — not failures):")
        lines.extend(warn)
        lines.append("")
    if dead:
        lines.append("Dead links (HTTP 404/410):")
        lines.extend(dead)
        lines.append("")
        lines.append(f"{len(dead)} dead link(s) found.")
    else:
        lines.append("No dead links found.")
    report = "\n".join(lines)
    print(report)
    (Path.cwd() / "linkcheck-agent-files.txt").write_text(report + "\n", encoding="utf-8")
    return 1 if dead else 0


if __name__ == "__main__":
    raise SystemExit(main())
