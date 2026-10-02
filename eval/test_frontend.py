"""Suite 6: the front end. The browser half (Playwright at 390, 1024 and 1440 px with axe and
the header checks) runs with `make e2e`; this half checks the built export and the copy."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "web" / "out"
PAGES = ["index", "ask", "compare", "before-after", "glossary", "governance", "operations", "about", "styleguide"]
sys.path.insert(0, str(ROOT / "scripts"))


def test_copy_and_comments_carry_no_banned_words():
    import authorship_lint

    assert authorship_lint.run() == []


@pytest.mark.skipif(not OUT.exists(), reason="run `make web` to build the static export")
def test_all_ten_pages_are_in_the_export():
    for page in PAGES:
        assert (OUT / f"{page}.html").exists(), page
    lineage = list((OUT / "lineage").glob("*.html"))
    glossary = json.loads((ROOT / "ontology" / "generated" / "glossary.json").read_text())
    assert {p.stem for p in lineage} == {g["metric_name"] for g in glossary}


@pytest.mark.skipif(not OUT.exists(), reason="run `make web` to build the static export")
def test_fonts_are_served_from_our_origin_with_their_licences():
    css = "".join(p.read_text() for p in (OUT / "_next" / "static" / "css").glob("*.css"))
    for font in ("fraunces-full.woff2", "instrument-sans.woff2", "jetbrains-mono.woff2"):
        assert f"/fonts/{font}" in css
        assert (OUT / "fonts" / font).exists()
    assert len(list((OUT / "fonts").glob("OFL-*.txt"))) == 3
    assert "fonts.googleapis" not in css and "fonts.gstatic" not in css


@pytest.mark.skipif(not OUT.exists(), reason="run `make web` to build the static export")
def test_no_page_loads_anything_from_another_origin():
    for html in OUT.rglob("*.html"):
        for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', html.read_text()):
            pytest.fail(f"{html.name} loads {url}")


def test_design_bans_are_not_in_the_styles():
    styles = "".join(p.read_text() for p in (ROOT / "web").glob("**/*.css") if "node_modules" not in str(p)
                     and "/out/" not in str(p) and ".next" not in str(p))
    components = "".join(p.read_text() for p in (ROOT / "web" / "components").glob("*.tsx"))
    pages = "".join(p.read_text() for p in (ROOT / "web" / "app").rglob("*.tsx"))
    for banned in ("linear-gradient", "radial-gradient", "backdrop-filter", "box-shadow:", "drop-shadow"):
        assert banned not in styles + components + pages, banned
    for banned in ("rounded-full", "rounded-lg", "rounded-xl", "shadow-", "bg-gradient", "backdrop-blur"):
        assert banned not in components + pages, banned
    assert "Powered by" not in components + pages


def test_tokens_meet_wcag_aa_for_every_text_pairing():
    def lum(hexcode: str) -> float:
        channels = [int(hexcode[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    def ratio(a: str, b: str) -> float:
        hi, lo = sorted((lum(a), lum(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    grounds = {"ground": "#0B0D10", "stratum": "#121519", "stratum-2": "#181C22"}
    text = {"bone": "#E9E4DA", "ash": "#9AA0A6", "ore": "#E36F2E", "good": "#6FCF97", "warn": "#F2C94C",
            "critical": "#EB5757"}
    for g, gv in grounds.items():
        for t, tv in text.items():
            assert ratio(gv, tv) >= 4.5, f"{t} on {g} is {ratio(gv, tv):.2f}"
    assert ratio("#F4F1EA", "#121212") >= 4.5


@pytest.mark.skipif(not (ROOT / "web" / "tests" / "screenshots").exists(), reason="run `make screenshots`")
def test_screenshots_exist_at_three_widths():
    shots = {p.stem for p in (ROOT / "web" / "tests" / "screenshots").glob("*.png")}
    for width in ("phone", "laptop", "desk"):
        assert any(s.startswith(f"{width}-") for s in shots), width
