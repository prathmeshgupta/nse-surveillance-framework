"""Surveillance Action Evaluator and Strategy Backtest Gate."""

import pandas as pd
from typing import Dict, Any, Optional

class SurveillanceEvaluator:
    """Evaluates whether an equity has execution restrictions or is forbidden to trade."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def check_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Checks if a symbol is currently under any surveillance restrictions."""
        sym_upper = symbol.upper()
        matches = self.df[self.df["symbol"] == sym_upper]
        if matches.empty:
            return None

        latest = matches.iloc[0]
        return {
            "symbol": sym_upper,
            "security_name": latest["security_name"],
            "series": latest["series"],
            "framework": latest["framework"],
            "circuit_band": latest["circuit_band"],
            "margin_requirement_pct": float(latest["margin_requirement_pct"]),
            "trading_restrictions": latest["trading_restrictions"],
            "is_intraday_allowed": latest["series"] not in ["BE", "BZ"],
            "is_execution_penalized": float(latest["margin_requirement_pct"]) > 20.0
        }

    def get_framework_summary(self) -> Dict[str, int]:
        """Returns total counts of scrips per surveillance framework."""
        return self.df["framework"].value_counts().to_dict()
