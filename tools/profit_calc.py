"""候補商品の1個あたり粗利を計算し、判定基準でGO/NGを付ける。

使い方:
    python3 tools/profit_calc.py data/candidates.csv [--out data/candidates_scored.csv]
"""

import argparse
import csv
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config" / "assumptions.toml"

REQUIRED = [
    "name", "category", "sell_price_jpy", "unit_cost_cny", "qty",
    "intl_shipping_total_jpy", "agent_fee_total_jpy", "duty_rate", "fba_fee_jpy",
]


def load_config(path=DEFAULT_CONFIG):
    with open(path, "rb") as f:
        return tomllib.load(f)


def referral_rate(row, cfg):
    if row.get("referral_rate"):
        return float(row["referral_rate"])
    rates = cfg["amazon"].get("referral_rates", {})
    return rates.get(row["category"], cfg["amazon"]["default_referral_rate"])


def evaluate(row, cfg):
    sell = float(row["sell_price_jpy"])
    qty = int(row["qty"])

    unit_cost = float(row["unit_cost_cny"]) * cfg["fx"]["cny_jpy"]
    shipping = float(row["intl_shipping_total_jpy"]) / qty
    agent_fee = float(row["agent_fee_total_jpy"]) / qty
    # 関税・輸入消費税の課税価格はCIF（商品代＋運賃）を基準にする
    cif = unit_cost + shipping
    duty = cif * float(row["duty_rate"])
    import_tax = (cif + duty) * cfg["costs"]["import_consumption_tax_rate"]
    landed = unit_cost + shipping + agent_fee + duty + import_tax

    referral = sell * referral_rate(row, cfg)
    fba = float(row["fba_fee_jpy"])
    per_item = cfg["amazon"].get("per_item_fee_jpy", 0)
    ad = sell * cfg["costs"]["ad_rate"]
    returns = sell * cfg["costs"]["return_rate"]

    profit = sell - referral - per_item - fba - ad - returns - landed
    margin = profit / sell
    th = cfg["thresholds"]
    reasons = []
    if margin < th["min_margin_rate"]:
        reasons.append(f"粗利率{margin:.1%}<{th['min_margin_rate']:.0%}")
    if profit < th["min_profit_jpy"]:
        reasons.append(f"粗利{profit:.0f}円<{th['min_profit_jpy']}円")

    return {
        "name": row["name"],
        "landed_cost_jpy": round(landed),
        "profit_jpy": round(profit),
        "margin_rate": round(margin, 3),
        "roi": round(profit / landed, 3),
        "batch_cost_jpy": round(landed * qty),
        "verdict": "GO" if not reasons else "NG",
        "reasons": " / ".join(reasons),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv")
    p.add_argument("--out")
    p.add_argument("--config", default=DEFAULT_CONFIG)
    args = p.parse_args(argv)
    cfg = load_config(args.config)

    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in REQUIRED if rows and c not in rows[0]]
    if missing:
        sys.exit(f"列が不足しています: {', '.join(missing)}")

    results = sorted((evaluate(r, cfg) for r in rows), key=lambda r: -r["profit_jpy"])
    total = sum(r["batch_cost_jpy"] for r in results if r["verdict"] == "GO")
    budget = cfg["thresholds"]["budget_total_jpy"]

    for r in results:
        print(f"[{r['verdict']}] {r['name']}: 粗利{r['profit_jpy']}円 "
              f"({r['margin_rate']:.1%}) 原価{r['landed_cost_jpy']}円 {r['reasons']}")
    print(f"GO品の仕入れ総額: {total:,}円 / 予算 {budget:,}円"
          + ("  ⚠ 予算超過" if total > budget else ""))

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)


if __name__ == "__main__":
    main()
