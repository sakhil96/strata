from __future__ import annotations

from api import narrate

LANDED = [{"name": "landed_cost_per_unit", "title": "landed cost per unit", "unit": "usd_per_unit"}]
OTD = [{"name": "on_time_delivery", "title": "on-time delivery", "unit": "ratio"}]


def answer(cards, dims, rows, start="2026-04-01", end="2026-09-01"):
    return {"canonical_query": {"metrics": [cards[0]["name"]], "dimensions": dims, "time": {"start": start, "end": end}},
            "metrics": cards, "rows": rows}


def test_a_single_value_reads_as_the_metric_its_value_and_its_window():
    lead = narrate.lead(answer(OTD, [], [{"on_time_delivery": 0.837553}], "2025-10-01"))
    assert lead == "On-time delivery was 83.8% for Oct 2025 to Sep 2026."


def test_a_monthly_series_that_turns_names_its_ends_its_change_and_its_low_and_high():
    costs = [156.31, 152.10, 149.20, 148.46, 156.00, 162.31]
    rows = [{"period_month": f"2026-{m:02d}-01", "landed_cost_per_unit": v} for m, v in zip(range(4, 10), costs, strict=True)]
    lead = narrate.lead(answer(LANDED, ["period_month"], rows))
    assert lead.startswith("Landed cost per unit rose from $156.31 in Apr 2026 to $162.31 in Sep 2026, up $6.00, 3.8%.")
    assert "The low was $148.46 in Jul 2026 and the high $162.31 in Sep 2026." in lead


def test_a_rate_moves_in_points_and_a_steady_series_says_nothing_about_turns():
    rows = [{"period_month": "2026-07-01", "on_time_delivery": 0.80}, {"period_month": "2026-08-01", "on_time_delivery": 0.82},
            {"period_month": "2026-09-01", "on_time_delivery": 0.85}]
    lead = narrate.lead(answer(OTD, ["period_month"], rows, "2026-07-01"))
    assert "up 5.0 points" in lead and "low" not in lead


def test_a_ranking_names_the_lowest_and_highest_without_judging_which_is_better():
    rows = [{"supplier_name": "Abbott", "on_time_delivery": 0.71}, {"supplier_name": "Brandt", "on_time_delivery": 0.93}]
    lead = narrate.lead(answer(OTD, ["supplier_name"], rows), "Which suppliers have the worst on-time receipt?",
                        {"supplier_name": "Supplier"})
    assert "Abbott is lowest" in lead and "Brandt highest at 93.0%" in lead and "2 supplier values" in lead


def test_markdown_never_survives_as_text():
    text = "**Read** `landed cost` as _landed_cost_per_unit_.\n\n| a | b |\n---\n```sql\nSELECT 1\n```"
    cleaned = narrate.plain(text)
    for mark in ("*", "`", "|", "---", "```", "SELECT"):
        assert mark not in cleaned, mark
    assert "landed_cost_per_unit" in cleaned


def test_a_reading_that_carries_an_amount_a_rate_or_a_hash_is_dropped():
    assert narrate.reading("It was $156.31 in April.") is None
    assert narrate.reading("On-time delivery was 83.8%.") is None
    assert narrate.reading("Hash 40e81be56d1a2b3c.") is None
    assert narrate.reading('." and for SQL results "All multi-row results: use <table>". The Response says no numbers.') is None
    kept = narrate.reading("I read landed cost by month from Apr to Sep 2026. No filters. A third sentence.")
    assert kept == "I read landed cost by month from Apr to Sep 2026. No filters."
