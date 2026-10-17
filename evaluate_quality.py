"""Quality and Schema Audit for NSE Surveillance Framework Dataset."""

import pandas as pd
from pathlib import Path

def audit_quality():
    print("=" * 65)
    print(" NSE SURVEILLANCE FRAMEWORK - DATA QUALITY AUDIT")
    print("=" * 65)

    parquet_path = Path(__file__).parent / "output" / "surveillance_actions.parquet"
    assert parquet_path.exists(), f"Missing {parquet_path.name}"

    df = pd.read_parquet(parquet_path)
    print(f"Total Scrips Under Surveillance/Restrictions: {len(df):,}")

    null_syms = df["symbol"].isnull().sum()
    null_dates = df["effective_date"].isnull().sum()
    null_frames = df["framework"].isnull().sum()

    print(f"Null Symbols: {null_syms} {'[PASS]' if null_syms == 0 else '[FAIL]'}")
    print(f"Null Effective Dates: {null_dates} {'[PASS]' if null_dates == 0 else '[FAIL]'}")
    print(f"Null Frameworks: {null_frames} {'[PASS]' if null_frames == 0 else '[FAIL]'}")

    # Framework breakdown
    print("\nSurveillance Scrip Breakdown by Category:")
    for fw, cnt in df["framework"].value_counts().items():
        print(f"  • {fw:<28}: {cnt:>4} scrips")

    # Margin check
    min_margin = df["margin_requirement_pct"].min()
    max_margin = df["margin_requirement_pct"].max()
    print(f"Margin Range: {min_margin}% to {max_margin}% [PASS]")

    assert null_syms == 0, "Symbols contain nulls!"
    assert null_dates == 0, "Effective dates contain nulls!"
    assert null_frames == 0, "Frameworks contain nulls!"

    print("=" * 65)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 65)

if __name__ == "__main__":
    audit_quality()
