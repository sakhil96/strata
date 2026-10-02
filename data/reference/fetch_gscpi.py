"""Fetch the Global Supply Chain Pressure Index into data/reference/gscpi.csv.

We do not commit the values: the New York Fed publishes them under its own terms of use,
which we could not confirm as public domain or CC BY. The file is fetched at build time.
"""

from __future__ import annotations

import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd

URL = "https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx"
OUT = Path(__file__).resolve().parent / "gscpi.csv"


def main() -> int:
    with urllib.request.urlopen(URL, timeout=30) as response:
        workbook = io.BytesIO(response.read())
    frame = pd.read_excel(workbook, sheet_name="GSCPI Monthly Data", usecols=[0, 1], names=["month_end", "gscpi"])
    frame = frame[pd.to_datetime(frame.month_end, errors="coerce", format="%d-%b-%Y").notna()]
    frame["month_end"] = pd.to_datetime(frame.month_end, format="%d-%b-%Y").dt.date
    frame.to_csv(OUT, index=False)
    print(f"wrote {len(frame)} months to {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
