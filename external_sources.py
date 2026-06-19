"""
External data sources for series that FRED's download API serves stale.

FRED's OECD-sourced euro-area unemployment and China CPI feeds are frozen
(Jan 2023 and Apr 2025 respectively). These functions pull fresh equivalents
from the official providers' free, keyless APIs:

  - Euro-area unemployment : Eurostat  (dataset une_rt_m, EA21, SA)
  - China CPI (YoY)         : IMF CPI via DBnomics (index -> computed YoY)

Each returns a pandas Series indexed by date, matching the shape fetch_series
expects, or None on failure (the agent then keeps the FRED fallback).
No API key required for either provider.
"""

import pandas as pd
import requests

EUROSTAT_UNE = ("https://ec.europa.eu/eurostat/api/dissemination/"
                "statistics/1.0/data/une_rt_m")
DBNOMICS_CN_CPI = ("https://api.db.nomics.world/v22/series/"
                   "IMF/CPI/M.CN.PCPI_IX?observations=1")


def ea_unemployment():
    """Euro-area (EA21) harmonised unemployment rate, %, seasonally adjusted."""
    try:
        params = {"format": "JSON", "geo": "EA21", "s_adj": "SA",
                  "age": "TOTAL", "sex": "T", "unit": "PC_ACT", "lang": "EN"}
        d = requests.get(EUROSTAT_UNE, params=params, timeout=40).json()
        idx = d["dimension"]["time"]["category"]["index"]   # {"2026-04": 519, ...}
        inv = {v: k for k, v in idx.items()}
        vals = d["value"]                                    # {"519": 6.3, ...}
        rows = []
        for k, v in vals.items():
            period = inv[int(k)]                             # "2026-04"
            rows.append((pd.Timestamp(period + "-01"), float(v)))
        if not rows:
            return None
        s = pd.Series(dict(rows)).sort_index()
        return s
    except Exception as e:
        print(f"  (Eurostat EA unemployment fetch failed: {e})")
        return None


def china_cpi_yoy():
    """China CPI year-over-year %, computed from the IMF monthly price index."""
    try:
        d = requests.get(DBNOMICS_CN_CPI, timeout=40).json()
        doc = d["series"]["docs"][0]
        periods = doc["period"]      # ["2025-06", "2025-07", ...]
        values = doc["value"]
        s_idx = pd.Series(
            [float(v) for v in values],
            index=[pd.Timestamp(p + "-01") for p in periods]
        ).sort_index().dropna()
        # year-over-year from the index (12 monthly steps)
        yoy = (s_idx.pct_change(12) * 100).dropna()
        return yoy if not yoy.empty else None
    except Exception as e:
        print(f"  (DBnomics China CPI fetch failed: {e})")
        return None


# maps FRED series id -> fresh external fetcher; the agent consults this
EXTERNAL_OVERRIDES = {
    "LRHUTTTTEZM156S": ("Eurostat", ea_unemployment),
    "CHNCPIALLMINMEI": ("IMF/DBnomics", china_cpi_yoy),
}


if __name__ == "__main__":
    s = ea_unemployment()
    print("EA unemployment latest:", s.index[-1].date(), "=", s.iloc[-1], "%")
    c = china_cpi_yoy()
    print("China CPI YoY latest:", c.index[-1].date(), "=", round(c.iloc[-1], 2), "%")
