import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import profit_calc  # noqa: E402

CFG = {
    "fx": {"cny_jpy": 20.0},
    "thresholds": {"min_margin_rate": 0.30, "min_profit_jpy": 500, "budget_total_jpy": 100000},
    "costs": {"ad_rate": 0.10, "return_rate": 0.0, "import_consumption_tax_rate": 0.10},
    "amazon": {"default_referral_rate": 0.15, "referral_rates": {"スポーツ&アウトドア": 0.10}},
}


def row(**kw):
    base = {
        "name": "t", "category": "スポーツ&アウトドア", "sell_price_jpy": "10000",
        "unit_cost_cny": "100", "qty": "10", "intl_shipping_total_jpy": "10000",
        "agent_fee_total_jpy": "0", "duty_rate": "0", "fba_fee_jpy": "500",
    }
    base.update(kw)
    return base


class EvaluateTest(unittest.TestCase):
    def test_breakdown(self):
        # 原価 = 2000 + 1000 + 輸入消費税300 = 3300
        # 粗利 = 10000 - 1000(手数料) - 500 - 1000(広告) - 3300 = 4200
        r = profit_calc.evaluate(row(), CFG)
        self.assertEqual(r["landed_cost_jpy"], 3300)
        self.assertEqual(r["profit_jpy"], 4200)
        self.assertEqual(r["verdict"], "GO")

    def test_duty_included_in_import_tax_base(self):
        r = profit_calc.evaluate(row(duty_rate="0.1"), CFG)
        # CIF 3000, 関税300, 輸入消費税 (3000+300)*0.1=330
        self.assertEqual(r["landed_cost_jpy"], 3630)

    def test_ng_on_low_margin(self):
        r = profit_calc.evaluate(row(sell_price_jpy="4000"), CFG)
        self.assertEqual(r["verdict"], "NG")
        self.assertIn("粗利率", r["reasons"])

    def test_default_referral_for_unknown_category(self):
        r = profit_calc.evaluate(row(category="不明"), CFG)
        self.assertEqual(r["profit_jpy"], 3700)

    def test_explicit_referral_overrides(self):
        r = profit_calc.evaluate(row(referral_rate="0.08"), CFG)
        self.assertEqual(r["profit_jpy"], 4400)


if __name__ == "__main__":
    unittest.main()
