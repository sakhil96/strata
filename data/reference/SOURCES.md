# Reference data sources

## HTS 2026 tariff schedule (hts_2026.csv)

Derived from the Harmonized Tariff Schedule published by the US International Trade
Commission (USITC). Public domain as a US government work. We include a simplified
extract with HTS codes relevant to the parts in our simulated ontology, not the full
schedule. Columns: hts_code, description, duty_rate, effective_from, effective_to.

The 2026-07-24 tariff step-up is a synthetic event for testing landed cost calculations
under changing duty rates.

## GSCPI (gscpi.csv)

Global Supply Chain Pressure Index, Federal Reserve Bank of New York. Monthly index
values used to calibrate the variance in supplier lead times and freight costs in the
data generator. Public data cited per the NY Fed's terms of use.

Source: https://www.newyorkfed.org/research/policy/gscpi

## FX rates

Generated deterministically from publicly known approximate exchange rates for
USD/EUR and USD/SGD. Not sourced from any proprietary feed.

## Industry benchmarks (not in repository)

The data generator's distributions for OTD (88-94%), OTIF (82-90%), fill rate (92-97%),
DOI (25-45 days) and inventory turns (8-15) are calibrated against publicly reported
benchmarks from:

- ASCM (formerly APICS) State of the Supply Chain reports
- Gartner Supply Chain Top 25 analysis
- Federal Reserve GSCPI commentary

No proprietary data is included. These are used only to set realistic distribution
parameters in generate.py.
