# Third-party notices

This project uses the following third-party materials.

## Fonts (SIL Open Font License 1.1)

- **Fraunces** — Phalanx (Flavia Zimbardi, Google Fonts). Display and large numerals.
- **Instrument Sans** — Rodrigo Fuenzalida, Google Fonts. Interface text.
- **JetBrains Mono** — JetBrains. Labels, hashes, SQL, timestamps, tabular numbers.

All fonts are self-hosted under the SIL Open Font License.

## Reference data

- **HTS 2026 tariff schedule** (`data/reference/hts_2026.csv`): derived from the
  publicly available Harmonized Tariff Schedule published by the US International Trade
  Commission. Public domain (US government work).
- **GSCPI**: Global Supply Chain Pressure Index, Federal Reserve Bank of New York. Not committed;
  `data/reference/fetch_gscpi.py` downloads it locally because redistribution terms are unconfirmed.
- **ISO 4217 currency codes**: ISO standard, referenced but not reproduced in full.
- **SCOR model attribute names**: ASCM Supply Chain Operations Reference model.
  Attribute names used descriptively under fair use.

## Calibration sources (not included in repository)

The data generator's distributions are calibrated against publicly reported industry
benchmarks. No proprietary datasets (DataCo, Brunel, USAID, Kaggle competition files)
are committed or required. See `data/reference/SOURCES.md` for the full list of
calibration references.

## Software dependencies

All software dependencies are listed in `pyproject.toml` (Python) and `web/package.json`
(Node.js). Licence compatibility is checked by `pip-audit` and `pnpm audit` in CI.
No copyleft dependencies are included in the runtime distribution.

## Software

Python dependencies are listed with versions and hashes in `requirements.lock` and
`requirements-dev.lock`; JavaScript dependencies in `web/package-lock.json`. CI emits CycloneDX SBOMs
for both. Principal components: FastAPI (MIT), Pydantic (MIT), DuckDB (MIT), dbt-core (Apache 2.0),
LinkML (CC0/Apache 2.0), snowflake-connector-python (Apache 2.0), Next.js (MIT), React (MIT),
Tailwind CSS (MIT), Framer Motion (MIT), visx (MIT), Playwright (Apache 2.0), axe-core (MPL 2.0).
