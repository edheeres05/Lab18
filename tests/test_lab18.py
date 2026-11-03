"""Regression tests; the answer key appears ONLY here, never in the data engine."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/skills/buffett-business/scripts"))
from sec_facts import (TAGS, analyze, annual_flow, audit_memo, display_value,
                       fiscal_ends, load_company, read_snapshot, save_snapshot,
                       select_fact, table_records, three_checks, year_row)


class Lab18Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cost_facts, cls.source = load_company("COST", ROOT / "data", offline=True)
        cls.cost = analyze(cls.cost_facts, "COST", cls.source)
        facts, source = load_company("JPM", ROOT / "data", offline=True)
        cls.jpm = analyze(facts, "JPM", source)

    def test_cost_every_answer_key_cell(self):
        expected = [
            ["2022-08-28", "226,954", "5,844", "7,392", "3,891", "20,642", "28.3%", "3,501"],
            ["2023-09-03", "242,290", "6,292", "11,068", "4,323", "25,058", "25.1%", "6,745"],
            ["2024-09-01", "254,453", "7,367", "11,339", "4,710", "23,622", "31.2%", "6,629"],
            ["2025-08-31", "275,235", "8,099", "13,335", "5,498", "29,164", "27.8%", "7,837"],
            ["2026-08-30", "303,154", "9,226", "15,817", "6,435", "35,803", "25.8%", "9,382"],
        ]
        self.assertEqual([list(r.values()) for r in table_records(self.cost)], expected)
        self.assertEqual(list(self.cost["checks"].values()), ["pass"] * 3)

    def test_jpm_missing_is_not_zero(self):
        for r in self.jpm["rows"]:
            self.assertIsNone(r["capital_spending"]["value"])
            self.assertIsNone(r["owner_earnings"]["value"])
        self.assertEqual(list(self.jpm["checks"].values()), ["fail", "not known", "not known"])

    def test_fiscal_end_not_filing_fy(self):
        facts = copy.deepcopy(self.cost_facts)
        for tag in facts["facts"]["us-gaap"].values():
            for values in tag.get("units", {}).values():
                for item in values:
                    item["fy"] = 9999
        self.assertEqual(fiscal_ends(facts), fiscal_ends(self.cost_facts))

    def test_latest_filing_wins(self):
        tag = "NetIncomeLoss"
        records = [dict(start="2025-01-01", end="2025-12-31", form="10-K", val=1,
                        filed="2026-02-01", accn="a"),
                   dict(start="2025-01-01", end="2025-12-31", form="10-K", val=2,
                        filed="2026-03-01", accn="b")]
        facts = {"facts": {"us-gaap": {tag: {"units": {"USD": records}}}}}
        self.assertEqual(select_fact(facts, (tag,), "2025-12-31")["value"], 2)
        records.reverse()
        self.assertEqual(select_fact(facts, (tag,), "2025-12-31")["value"], 2)

    def test_quarters_other_forms_and_multiyear_rejected(self):
        for form, start in [("10-Q", "2025-01-01"), ("10-K/A", "2025-01-01"),
                            ("10-K", "2025-10-01"), ("10-K", "2024-01-01")]:
            self.assertFalse(annual_flow({"form": form, "start": start, "end": "2025-12-31"}))
        self.assertTrue(annual_flow({"form": "10-K", "start": "2022-08-29", "end": "2023-09-03"}))

    def test_tag_fallback_is_per_year(self):
        first, second = TAGS["revenue"]
        f = dict(start="2025-01-01", end="2025-12-31", form="10-K", val=123,
                 filed="2026-02-01", accn="a")
        facts = {"facts": {"us-gaap": {
            first: {"units": {"USD": [dict(f, end="2024-12-31", start="2024-01-01")]}},
            second: {"units": {"USD": [f]}}}}}
        self.assertEqual(select_fact(facts, TAGS["revenue"], "2025-12-31")["tag"], "us-gaap:" + second)

    def test_primary_tag_has_priority(self):
        first, second = TAGS["revenue"]
        f = dict(start="2025-01-01", end="2025-12-31", form="10-K", val=123, filed="2026-02-01")
        facts = {"facts": {"us-gaap": {
            first: {"units": {"USD": [f]}},
            second: {"units": {"USD": [dict(f, val=999, filed="2026-03-01")]}}}}}
        self.assertEqual(select_fact(facts, TAGS["revenue"], "2025-12-31")["value"], 123)

    def test_nonpositive_equity(self):
        for equity in [0, -100]:
            f = dict(end="2025-12-31", form="10-K", val=equity, filed="2026-02-01")
            facts = {"facts": {"us-gaap": {
                "StockholdersEquity": {"units": {"USD": [f]}},
                "NetIncomeLoss": {"units": {"USD": [dict(f, val=10, start="2025-01-01")]}}}}}
            row = year_row(facts, "2025-12-31")
            self.assertIsNone(row["roe"]["value"])
            self.assertEqual(list(three_checks([row] * 5).values())[0], "not known")

    def test_threshold_uses_unrounded_ratio(self):
        rows = copy.deepcopy(self.cost["rows"])
        rows[0]["net_income"]["value"] = 14999
        rows[0]["equity"]["value"] = 100000
        rows[0]["roe"]["value"] = 0.14999
        self.assertEqual(display_value("roe", 0.14999), "15.0%")
        self.assertEqual(list(three_checks(rows).values())[0], "fail")

    def test_missing_check_input_is_unknown(self):
        rows = copy.deepcopy(self.cost["rows"])
        rows[0]["owner_earnings"]["value"] = None
        rows[1]["owner_earnings"]["value"] = -1
        self.assertEqual(list(three_checks(rows).values())[1:], ["not known", "not known"])

    def test_growth_checks_endpoints_not_monotonicity(self):
        self.assertLess(self.cost["rows"][2]["owner_earnings"]["value"], self.cost["rows"][1]["owner_earnings"]["value"])
        self.assertEqual(list(self.cost["checks"].values())[2], "pass")

    def test_missing_year_not_invented(self):
        self.assertEqual(list(three_checks(self.cost["rows"][:4]).values()), ["not known"] * 3)

    def test_numeric_probe_flags_every_occurrence(self):
        flags = audit_memo("ROE was 40.0%.\nAgain: 40.0% and 999.\nNot printed: .12345 and 4e1%.", self.cost)
        self.assertEqual([f["number"] for f in flags], ["40.0%", "40.0%", "999", ".12345", "4e1%"])
        self.assertEqual(flags[0]["line"], 1)

    def test_percentage_not_interchangeable_with_money(self):
        self.assertTrue(audit_memo("Owner earnings: 3,501%", self.cost))
        self.assertTrue(audit_memo("ROE: 28.3", self.cost))
        self.assertFalse(audit_memo("ROE: 28.30%. Owner earnings: 3501.0.", self.cost))

    def test_saved_memos_pass_audit(self):
        for result in [self.cost, self.jpm]:
            memo = (ROOT / "reports" / f'{result["ticker"]}_memo.md').read_text(encoding="utf-8")
            self.assertEqual(audit_memo(memo, result), [])

    def test_snapshot_tampering_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "facts.json"
            save_snapshot(p, b'{"cik": 1}', "https://data.sec.gov/example")
            p.write_text('{"cik": 2}')
            with self.assertRaises(ValueError):
                read_snapshot(p)


if __name__ == "__main__":
    unittest.main()
