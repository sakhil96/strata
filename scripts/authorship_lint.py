"""Fail on machine-made fingerprints: banned words in comments and in user-facing copy.

Comments may not say generated, AI, assistant, here is, example, placeholder, sample, TODO,
lorem, foo or bar. The compiler's one header line is the single exception. Front-end copy may
not use marketing verbs, exclamation marks or emoji.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = "Generated from ontology/*.yaml by compile.py; edit the registry, not this file."
COMMENT_BANS = re.compile(r"\b(generated|AI|assistant|here is|example|placeholder|sample|TODO|lorem|foo|bar)\b", re.I)
AI_TOKEN = re.compile(r"\bAI\b")
COPY_BANS = re.compile(r"\b(seamless(ly)?|robust|leverag(e|es|ing)|unlock(s|ing)?|empower(s|ing)?|supercharg(e|es|ing))\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\U0001F000-\U0001F2FF]")
SKIP = ("node_modules", ".next", "/out/", ".venv", "dbt/target", "data/out", "ontology/generated", "cube/model",
        "snowflake/semantic", "web/public", "test-results", "playwright-report", ".git/", "scripts/authorship_lint.py")
COMMENT_STYLES = {
    ".py": [r"#(.*)$", r'^\s*"""(.*?)"""', r"^\s*'''(.*?)'''"],
    ".sql": [r"--(.*)$", r"\{#(.*?)#\}"],
    ".ts": [r"//(.*)$", r"/\*(.*?)\*/"],
    ".tsx": [r"//(.*)$", r"/\*(.*?)\*/", r"\{/\*(.*?)\*/\}"],
    ".mjs": [r"//(.*)$", r"/\*(.*?)\*/"],
    ".css": [r"/\*(.*?)\*/"],
    ".yml": [r"#(.*)$"],
    ".yaml": [r"#(.*)$"],
}


def files() -> list[Path]:
    out = []
    for ext in COMMENT_STYLES:
        for path in ROOT.rglob(f"*{ext}"):
            rel = path.relative_to(ROOT).as_posix()
            if not any(s.strip("/") in rel for s in SKIP):
                out.append(path)
    return sorted(out)


def comment_findings(path: Path) -> list[str]:
    text = path.read_text(errors="ignore")
    findings = []
    for pattern in COMMENT_STYLES[path.suffix]:
        flags = re.M | (re.S if "*?" in pattern else 0)
        for m in re.finditer(pattern, text, flags):
            comment = m.group(1)
            if HEADER in comment or comment.strip().startswith(("!", "noqa", "type:")):
                continue
            # URLs and code inside comments are not prose.
            prose = re.sub(r"https?://\S+|`[^`]*`|[A-Z_]{3,}\(|\bAI_[A-Z_]+", " ", comment)
            hit = COMMENT_BANS.search(prose)
            if hit and (hit.group(0).upper() != "AI" or AI_TOKEN.search(prose)):
                line = text.count("\n", 0, m.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: comment says {hit.group(0)!r}")
    return findings


def copy_findings(path: Path) -> list[str]:
    if path.suffix not in (".tsx",) or "/tests/" in path.as_posix():
        return []
    text = re.sub(r"/\*.*?\*/|//[^\n]*", " ", path.read_text(), flags=re.S)
    findings = []
    strings = re.findall(r">([^<>{}]+)<|\"([^\"]{3,})\"|`([^`]{3,})`", text)
    for groups in strings:
        s = next(g for g in groups if g)
        if COPY_BANS.search(s):
            findings.append(f"{path.relative_to(ROOT)}: copy uses {COPY_BANS.search(s).group(0)!r}: {s.strip()[:60]}")
        if re.search(r"[A-Za-z]!(\s|$)", s) and "!=" not in s:
            findings.append(f"{path.relative_to(ROOT)}: copy has an exclamation mark: {s.strip()[:60]}")
        if EMOJI.search(s):
            findings.append(f"{path.relative_to(ROOT)}: copy has an emoji: {s.strip()[:60]}")
    return findings


def run() -> list[str]:
    found = []
    for path in files():
        found += comment_findings(path) + copy_findings(path)
    return found


if __name__ == "__main__":
    problems = run()
    print("\n".join(problems) or "authorship lint: clean")
    sys.exit(1 if problems else 0)
