"""NSE Surveillance Framework Weekly/Daily Automated Updater.

Fetches active ASM, GSM, ESM, and Trade-for-Trade regulatory restrictions
from official NSE feeds, deduplicates state transitions, and exports Parquet/CSV.
"""

import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

# Add local src to path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nse_surveillance_framework.fetcher import SurveillanceFetcher

def update_surveillance_framework():
    print(f"[{datetime.now().isoformat()}] Starting Surveillance Framework update...")
    fetcher = SurveillanceFetcher()
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_file = output_dir / "surveillance_actions.csv"
    parquet_file = output_dir / "surveillance_actions.parquet"

    existing_df = pd.DataFrame()
    if parquet_file.exists():
        existing_df = pd.read_parquet(parquet_file)
        print(f"Loaded {len(existing_df):,} existing surveillance records from {parquet_file.name}")

    print("Fetching active surveillance and price band restrictions from NSE...")
    new_df = fetcher.fetch_active_surveillance()

    if new_df.empty and existing_df.empty:
        raise RuntimeError("No surveillance data retrieved and no existing database found.")

    combined = []
    if not existing_df.empty:
        combined.append(existing_df)
    if not new_df.empty:
        print(f"Retrieved {len(new_df):,} active surveillance scrips.")
        combined.append(new_df)

    merged = pd.concat(combined, ignore_index=True)

    # Core key deduplication
    merged = merged.drop_duplicates(subset=["effective_date", "symbol", "framework"], keep="last")

    # Sort deterministically
    merged = merged.sort_values(by=["effective_date", "framework", "symbol"], ascending=[False, True, True]).reset_index(drop=True)

    # Save
    merged.to_parquet(parquet_file, index=False, compression="snappy")
    merged.to_csv(csv_file, index=False)
    print(f"Saved {len(merged):,} records to {parquet_file.name} and {csv_file.name}")

    # Run quality gate
    from evaluate_quality import audit_quality
    audit_quality()
    print("Surveillance Framework update completed successfully.")

if __name__ == "__main__":
    update_surveillance_framework()
