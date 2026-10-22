"""月次の実績から事業利益・実質時給を計算し、どのハードルを満たしたかを判定する。

使い方:
    python3 tools/hurdle_check.py [data/monthly.csv]

CSVの列: month, revenue_jpy, gross_profit_jpy, hours
"""

import argparse
import csv
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config" / "assumptions.toml"
DEFAULT_CSV = ROOT / "data" / "monthly.csv"


def load_config(path=DEFAULT_CONFIG):
    with open(path, "rb") as f:
        return tomllib.load(f)


def evaluate_month(row, cfg):
    h = cfg["hurdles"]
    revenue = float(row["revenue_jpy"])
    gross = float(row["gross_profit_jpy"])
    hours = float(row["hours"])
    fixed = sum(cfg["fixed_costs"].values())

    margin = gross / revenue if revenue else 0.0
    profit = gross - fixed
    hourly = profit / hours if hours else 0.0

    stage1 = margin >= h["stage1_min_realized_margin"]
    stage2 = stage1 and hourly >= h["min_hourly_jpy"]
    stage3 = stage2 and profit >= h["stage3_min_monthly_profit_jpy"]
    return {
        "month": row["month"],
        "margin_rate": round(margin, 3),
        "profit_jpy": round(profit),
        "hourly_jpy": round(hourly),
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
    }


def trailing_streak(results, key):
    n = 0
    for r in reversed(results):
        if not r[key]:
            break
        n += 1
    return n


def judge(results, cfg):
    """直近の連続達成月数から、合格している最も高い段階を返す（0は未達）。"""
    h = cfg["hurdles"]
    if trailing_streak(results, "stage3") >= h["stage3_consecutive_months"]:
        return 3
    if trailing_streak(results, "stage2") >= h["stage2_consecutive_months"]:
        return 2
    if results and results[-1]["stage1"]:
        return 1
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv", nargs="?", default=DEFAULT_CSV)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    args = p.parse_args(argv)
    cfg = load_config(args.config)

    with open(args.csv, newline="", encoding="utf-8") as f:
        results = [evaluate_month(r, cfg) for r in csv.DictReader(f)]

    for r in results:
        marks = "".join("○" if r[f"stage{i}"] else "×" for i in (1, 2, 3))
        print(f"{r['month']}: 粗利率{r['margin_rate']:.1%} 事業利益{r['profit_jpy']:,}円 "
              f"実質時給{r['hourly_jpy']:,}円 [①②③ {marks}]")
    stage = judge(results, cfg)
    print(f"判定: {'①〜③のいずれも未達' if stage == 0 else '①②③'[stage - 1] + 'を合格'}")


if __name__ == "__main__":
    main()
