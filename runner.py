"""CLI Tool for NSE Surveillance Framework.

Usage:
    python runner.py --symbol ACSTECH
    python runner.py --framework GSM
    python runner.py --summary
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from nse_surveillance_framework.evaluator import SurveillanceEvaluator

def main():
    parser = argparse.ArgumentParser(description="NSE Surveillance Framework CLI")
    parser.add_argument("--symbol", help="Target equity ticker")
    parser.add_argument("--framework", help="Filter by framework (TRADE_FOR_TRADE_T2T, GSM, ASM, ESM, CURTAILED_PRICE_BAND)")
    parser.add_argument("--summary", action="store_true", help="Show summary of all scrips currently under surveillance")
    args = parser.parse_args()

    parquet_path = Path(__file__).parent / "output" / "surveillance_actions.parquet"
    if not parquet_path.exists():
        print("Dataset not found. Run python update.py first.")
        return

    df = pd.read_parquet(parquet_path)
    evaluator = SurveillanceEvaluator(df)

    if args.symbol:
        res = evaluator.check_symbol(args.symbol)
        if not res:
            print(f"\n[CLEAR] {args.symbol.upper()} is NOT under any active NSE surveillance framework.")
            print("  Standard trading and margin rules apply.\n")
        else:
            print(f"\n[ALERT] {args.symbol.upper()} is UNDER ACTIVE SURVEILLANCE / RESTRICTIONS:")
            for k, v in res.items():
                print(f"  * {k:<25}: {v}")
            print()

    elif args.framework:
        fw_df = df[df["framework"] == args.framework.upper()]
        if fw_df.empty:
            print(f"No scrips found under framework {args.framework.upper()}.")
            return
        print(f"\n--- Scrips under {args.framework.upper()} ({len(fw_df)} found) ---")
        cols = ["symbol", "series", "security_name", "circuit_band", "margin_requirement_pct", "trading_restrictions"]
        print(fw_df[cols].to_string(index=False))

    else:
        summary = evaluator.get_framework_summary()
        latest_date = df["effective_date"].max()
        print(f"\n==========================================================================")
        print(f" NSE SURVEILLANCE FRAMEWORK SUMMARY AS OF {latest_date}")
        print(f"==========================================================================")
        print(f"Total Scrips Under Regulatory Friction / Scrutiny: {len(df):,}\n")
        for fw, count in summary.items():
            print(f"  * {fw:<28}: {count:>4} scrips")
        print(f"==========================================================================\n")
        print("Use --symbol <TICKER> to check specific scrip or --framework <FRAMEWORK> to inspect list.")

if __name__ == "__main__":
    main()
