#!/usr/bin/env python3
"""Extract a single `[X.Y.Z]` block from CHANGELOG.md.

Skill-shipped template (v5 first-run-bootstrap deliverable). Wired
into `.github/workflows/verify-changelog.yml` so every push to main
or PR targeting main verifies the next-version's CHANGELOG block
exists before tagging.

Mitigates the failure mode where `release.yml` fires at tag time,
PyPI publish succeeds (IRREVERSIBLE), and then the CHANGELOG-extract
step fails — forcing a move-tag re-fire. See Evidentia v0.10.3 ship
incident 2026-05-23 for the canonical example.

Usage:

    python scripts/extract_changelog_block.py 0.10.3

Reads `CHANGELOG.md` from the repo root, locates the
`## [0.10.3] - <date>` heading, captures every line until the next
`## [` heading (or EOF), strips the heading line itself, and prints
the captured block to stdout.

Exit codes:
- 0 - block found + emitted
- 1 - no matching block found (release.yml fails fast)
- 2 - CLI usage error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_block(changelog_text: str, version: str) -> str | None:
    """Return the lines between `## [<version>]` and the next `## [`
    heading, exclusive of both heading lines."""
    start_pattern = re.compile(
        rf"^## \[{re.escape(version)}\][ \-].*$",
        re.MULTILINE,
    )
    next_heading_pattern = re.compile(r"^## \[", re.MULTILINE)

    start = start_pattern.search(changelog_text)
    if start is None:
        return None

    rest = changelog_text[start.end():]
    next_heading = next_heading_pattern.search(rest)
    block = rest[:next_heading.start()] if next_heading else rest

    return block.strip("\n")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>", file=sys.stderr)
        return 2

    version = sys.argv[1]
    changelog = Path("CHANGELOG.md")
    if not changelog.exists():
        print(f"ERROR: CHANGELOG.md not found in {Path.cwd()}", file=sys.stderr)
        return 1

    text = changelog.read_text(encoding="utf-8")
    block = extract_block(text, version)
    if block is None:
        print(f"ERROR: no [{version}] block found in CHANGELOG.md", file=sys.stderr)
        return 1

    print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
