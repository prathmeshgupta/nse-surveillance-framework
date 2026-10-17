# NSE Surveillance Framework Registry

[![Daily/Weekly Surveillance Dataset Update](https://github.com/prathmeshgupta/nse-surveillance-framework/actions/workflows/weekly_update.yml/badge.svg)](https://github.com/prathmeshgupta/nse-surveillance-framework/actions/workflows/weekly_update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Point-in-Time surveillance and regulatory restriction dataset for the National Stock Exchange of India (NSE). 

Tracks securities under **Additional Surveillance Measure (ASM)**, **Graded Surveillance Measure (GSM)**, **Enhanced Surveillance Measure (ESM)**, and **Trade-for-Trade (T2T / BE Series)** to eliminate critical lookahead and execution bias from quantitative backtests.

---

### The Quantitative Problem (The Backtest Trap)

In Indian small-cap, breakout, and momentum strategies, backtests frequently show spectacular hypothetical returns on volatile scrips that were **legally or practically impossible to execute in real-time**:

1. **ASM (Additional Surveillance Measure):**
   - Stage I to IV.
   - Requires **100% upfront cash margin** (broker intraday leverage is strictly disabled).
   - Price bands are compressed to **5%**.
2. **GSM (Graded Surveillance Measure):**
   - Imposes **Additional Surveillance Deposit (ASD)** up to **100% of trade value** (held by the exchange for 5 months without interest!).
   - In higher stages, trading is restricted to **once a week (Monday only)** or once a month via call auctions.
3. **Trade-to-Trade (T2T / BE Series):**
   - Intraday square-off is prohibited. Every buy transaction requires 100% funds and Demat delivery.

Without a historical surveillance filter, systematic algorithms attempt to buy stocks that are under regulatory freeze or severe margin penalty.

---

### Dataset Schema

Outputs are distributed in both **Apache Parquet (`snappy` compressed)** and standard **CSV**:
* `output/surveillance_actions.parquet`
* `output/surveillance_actions.csv`

| Field | Type | Description |
| :--- | :--- | :--- |
| `effective_date` | `string` | Circular / effective date in `YYYY-MM-DD` |
| `symbol` | `string` | NSE Trading Symbol (e.g. `ABAN`, `ACSTECH`) |
| `series` | `string` | Trading series (`BE`, `BZ`, `ST`, `EQ`) |
| `security_name` | `string` | Full corporate name of the equity |
| `framework` | `string` | Surveillance category (`ASM`, `GSM`, `ESM`, `TRADE_FOR_TRADE_T2T`, `CURTAILED_PRICE_BAND`) |
| `circuit_band` | `string` | Dynamic daily price band (`2%`, `5%`, `10%`) |
| `margin_requirement_pct` | `float` | Mandatory upfront margin (`100.0%` for surveillance scrips) |
| `trading_restrictions` | `string` | Execution friction details |
| `source` | `string` | Data source origin (`NSE_SEC_LIST_SURVEILLANCE`) |

---

### Automated Weekly & Daily Updates

* **Schedule**: Automated GitHub Actions workflow executes at **15:30 UTC (21:00 IST) Monday to Friday**, with a Sunday reconciliation at **02:00 UTC**.
* **Integrity Gate**: Enforces zero nulls in `symbol`, `framework`, and `effective_date`.

---

### Quickstart & CLI Usage

```bash
# 1. Clone the repository
git clone https://github.com/prathmeshgupta/nse-surveillance-framework.git
cd nse-surveillance-framework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated updater locally
python update.py

# 4. Check if a ticker has execution restrictions
python runner.py --symbol ACSTECH

# 5. View surveillance framework breakdown
python runner.py --summary

# 6. List all scrips under Trade-for-Trade (T2T)
python runner.py --framework TRADE_FOR_TRADE_T2T
```
