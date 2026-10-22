import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import hurdle_check  # noqa: E402

CFG = {
    "hurdles": {
        "stage1_min_realized_margin": 0.20,
        "min_hourly_jpy": 5000,
        "stage2_consecutive_months": 2,
        "stage3_min_monthly_profit_jpy": 100000,
        "stage3_consecutive_months": 3,
    },
    "fixed_costs": {"claude_jpy": 30000, "amazon_pro_jpy": 5000},
}


def month(m, revenue, gross, hours):
    return hurdle_check.evaluate_month(
        {"month": m, "revenue_jpy": revenue, "gross_profit_jpy": gross, "hours": hours}, CFG)


class HurdleTest(unittest.TestCase):
    def test_profit_and_hourly(self):
        r = month("2027-01", 400000, 95000, 12)
        self.assertEqual(r["profit_jpy"], 60000)
        self.assertEqual(r["hourly_jpy"], 5000)
        self.assertTrue(r["stage2"])
        self.assertFalse(r["stage3"])

    def test_low_margin_fails_everything(self):
        r = month("2027-01", 1000000, 150000, 5)
        self.assertFalse(r["stage1"])
        self.assertFalse(r["stage3"])

    def test_stage3_requires_hourly(self):
        # 事業利益10万円でも、30時間かけていれば時給約3,333円で③は不合格
        r = month("2027-01", 600000, 135000, 30)
        self.assertEqual(r["profit_jpy"], 100000)
        self.assertFalse(r["stage3"])

    def test_judge_uses_trailing_streak(self):
        good = month("m", 600000, 135000, 20)
        bad = month("m", 600000, 50000, 20)
        self.assertEqual(hurdle_check.judge([good, good, good], CFG), 3)
        self.assertEqual(hurdle_check.judge([good, bad, good, good], CFG), 2)
        self.assertEqual(hurdle_check.judge([good, bad, good], CFG), 1)
        self.assertEqual(hurdle_check.judge([], CFG), 0)


if __name__ == "__main__":
    unittest.main()
