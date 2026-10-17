"""NSE Surveillance Framework Fetcher.

Downloads and parses active surveillance lists (ASM, GSM, ESM, and Trade-for-Trade)
from NSE archives and circular feeds to identify regulatory execution restrictions.
"""

import io
import requests
import pandas as pd
from datetime import datetime, date
from typing import Optional, List

NSE_SEC_LIST_URL = "https://nsearchives.nseindia.com/content/equities/sec_list.csv"
NSE_CIRCULARS_URL = "https://www.nseindia.com/api/circulars?cat=Surveillance"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class SurveillanceFetcher:
    """Fetches active surveillance scrips and restrictions across NSE."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._primed = False

    def _prime_session(self):
        if not self._primed:
            try:
                self.session.get("https://www.nseindia.com", timeout=10)
                self._primed = True
            except:
                pass

    def fetch_active_surveillance(self) -> pd.DataFrame:
        """Fetches active scrips placed under surveillance or Trade-to-Trade."""
        records = []

        # 1. Fetch official sec_list.csv (Trade-to-Trade and Price Band restrictions)
        try:
            resp = self.session.get(NSE_SEC_LIST_URL, timeout=15)
            if resp.status_code == 200:
                df_sec = pd.read_csv(io.StringIO(resp.text))
                df_sec.columns = [c.strip() for c in df_sec.columns]

                # Strip whitespace
                for c in df_sec.columns:
                    df_sec[c] = df_sec[c].astype(str).str.strip()

                # Filter for scrips with restrictive bands (2, 5) or non-EQ series (BE, BZ, SM)
                surv_mask = df_sec["Series"].isin(["BE", "BZ", "ST"]) | df_sec["Band"].isin(["2", "5"])
                df_surv = df_sec[surv_mask].copy()

                today_str = date.today().strftime("%Y-%m-%d")

                for _, row in df_surv.iterrows():
                    sym = row["Symbol"]
                    series = row["Series"]
                    name = row["Security Name"]
                    band = row["Band"]
                    remarks = row.get("Remarks", "-")

                    # Classify framework
                    if "GSM" in remarks.upper():
                        framework = "GSM"
                        margin = 100.0
                        restrictions = "Graded Surveillance Measure: Additional surveillance deposit and periodic call auctions"
                    elif "ASM" in remarks.upper():
                        framework = "ASM"
                        margin = 100.0
                        restrictions = "Additional Surveillance Measure: 100% margin, price band curtailed"
                    elif "ESM" in remarks.upper():
                        framework = "ESM"
                        margin = 100.0
                        restrictions = "Enhanced Surveillance Measure: 2% band, 100% margin"
                    elif series in ["BE", "BZ"]:
                        framework = "TRADE_FOR_TRADE_T2T"
                        margin = 100.0
                        restrictions = "Compulsory delivery settlement (no intraday netting permitted)"
                    else:
                        framework = "CURTAILED_PRICE_BAND"
                        margin = 100.0 if band in ["2", "5"] else 20.0
                        restrictions = f"Narrow {band}% dynamic daily price band"

                    records.append({
                        "effective_date": today_str,
                        "symbol": sym,
                        "series": series,
                        "security_name": name,
                        "framework": framework,
                        "circuit_band": band,
                        "margin_requirement_pct": margin,
                        "trading_restrictions": restrictions,
                        "source": "NSE_SEC_LIST_SURVEILLANCE"
                    })
        except Exception as e:
            print(f"Error fetching sec_list surveillance: {e}")

        if not records:
            return pd.DataFrame()

        df_out = pd.DataFrame(records)
        df_out = df_out.drop_duplicates(subset=["effective_date", "symbol", "framework"])
        return df_out
