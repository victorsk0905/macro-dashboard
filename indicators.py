"""
Indicator configuration for the Macro Dashboard Agent.

Every series is pulled from FRED (one free API key covers all of them).
Get a free key in ~30 seconds at: https://fredaccount.stlouisfed.org/apikeys

Each indicator declares:
  id        : FRED series ID
  label     : human-readable name
  group     : dashboard cluster
  unit      : how to display the value
  freq      : reporting frequency (for context)
  transform : None | 'yoy_pct'  (yoy_pct = year-over-year % change, for price indices)
  good      : direction that is "healthy" -> 'up', 'down', or None (neutral/context-only)
  note      : one-line plain-English meaning
"""

INDICATORS = [
    # ---------------- GROWTH ----------------
    dict(id="GDPC1", label="US Real GDP Growth (annualized)", group="Growth", unit="qoq_annualized",
         freq="Quarterly", transform="qoq_annualized", good="up",
         note="Quarterly change in total US output, annualized. Positive = expanding, negative = contracting."),
    dict(id="UNRATE", label="US Unemployment Rate", group="Growth", unit="pct",
         freq="Monthly", transform=None, good="down",
         note="Share of the labor force without work. Rising = cooling/weakening economy."),
    dict(id="ICSA", label="US Initial Jobless Claims", group="Growth", unit="count_k",
         freq="Weekly", transform=None, good="down",
         note="New unemployment filings each week. The fastest real-time read on the labor market."),
    dict(id="INDPRO", label="US Industrial Production", group="Growth", unit="index_yoy",
         freq="Monthly", transform="yoy_pct", good="up",
         note="Output of factories, mines and utilities. A proxy for the real economy's momentum."),

    # ---------------- INFLATION & MONEY ----------------
    dict(id="CPIAUCSL", label="US CPI (Headline, YoY)", group="Inflation & Money", unit="pct",
         freq="Monthly", transform="yoy_pct", good="down",
         note="Cost of a typical basket of goods vs a year ago. The headline inflation number."),
    dict(id="CPILFESL", label="US Core CPI (YoY)", group="Inflation & Money", unit="pct",
         freq="Monthly", transform="yoy_pct", good="down",
         note="CPI excluding food & energy. Shows the underlying inflation trend."),
    dict(id="PCEPILFE", label="US Core PCE (YoY)", group="Inflation & Money", unit="pct",
         freq="Monthly", transform="yoy_pct", good="down",
         note="The Fed's preferred inflation gauge. Target is 2%; above that pressures rate policy."),
    dict(id="M2SL", label="US M2 Money Supply (YoY)", group="Inflation & Money", unit="pct",
         freq="Monthly", transform="yoy_pct", good=None,
         note="How fast the money stock is growing. Rapid growth can fuel inflation / asset prices."),

    # ---------------- RATES & POLICY ----------------
    dict(id="FEDFUNDS", label="US Fed Funds Rate", group="Rates & Policy", unit="pct",
         freq="Monthly", transform=None, good=None,
         note="The Fed's policy interest rate. Higher = tighter money to fight inflation."),
    dict(id="DGS10", label="US 10Y Treasury Yield", group="Rates & Policy", unit="pct",
         freq="Daily", transform=None, good=None,
         note="Benchmark long-term borrowing cost. Drives mortgages, corporate debt, valuations."),
    dict(id="T10Y2Y", label="US Yield Curve (10Y-2Y)", group="Rates & Policy", unit="pct",
         freq="Daily", transform=None, good="up",
         note="Long minus short rates. Negative (inverted) has preceded most recessions."),
    dict(id="BAMLH0A0HYM2", label="US High-Yield Credit Spread", group="Rates & Policy", unit="pct",
         freq="Daily", transform=None, good="down",
         note="Extra yield investors demand on risky corporate debt. Widening = stress building."),

    # ---------------- MARKETS & CURRENCY ----------------
    dict(id="DTWEXBGS", label="US Dollar Index (Broad)", group="Markets & Currency", unit="index",
         freq="Daily", transform=None, good=None,
         note="Trade-weighted strength of the USD vs major partners. Falling = dollar depreciation."),
    dict(id="VIXCLS", label="VIX (Volatility Index)", group="Markets & Currency", unit="index",
         freq="Daily", transform=None, good="down",
         note="The market's 'fear gauge'. <20 calm, >30 stress, >40 panic."),
    dict(id="DCOILWTICO", label="Crude Oil (WTI)", group="Markets & Currency", unit="usd",
         freq="Daily", transform=None, good=None,
         note="Energy cost input to the whole economy. Spikes feed inflation; crashes signal demand fear."),
    dict(id="SP500", label="S&P 500", group="Markets & Currency", unit="index",
         freq="Daily", transform=None, good="up",
         note="Broad US equity benchmark and a barometer of risk appetite."),

    # ---------------- GLOBAL ----------------
    dict(id="CP0000EZ19M086NEST", label="Euro Area Inflation (HICP YoY)", group="Global", unit="pct",
         freq="Monthly", transform="yoy_pct", good="down",
         note="Eurozone consumer inflation. Drives ECB policy and the EUR/USD rate."),
    dict(id="LRHUTTTTEZM156S", label="Euro Area Unemployment", group="Global", unit="pct",
         freq="Monthly", transform=None, good="down",
         note="Eurozone labor market health."),
    dict(id="ECBDFR", label="ECB Deposit Rate", group="Global", unit="pct",
         freq="Daily", transform=None, good=None,
         note="The ECB's main policy rate. The euro-side counterpart to the Fed funds rate."),
    dict(id="CHNCPIALLMINMEI", label="China CPI (YoY)", group="Global", unit="pct",
         freq="Monthly", transform="yoy_pct", good=None,
         note="China consumer inflation. Near zero / negative signals weak domestic demand."),
    dict(id="DEXCHUS", label="China Yuan per USD", group="Global", unit="fx",
         freq="Daily", transform=None, good=None,
         note="CNY/USD exchange rate. A managed proxy for China's growth & capital-flow pressure."),
    dict(id="DEXINUS", label="India Rupee per USD", group="Global", unit="fx",
         freq="Daily", transform=None, good=None,
         note="INR/USD. A read on a major emerging market and broad EM currency pressure."),
]

GROUP_ORDER = ["Growth", "Inflation & Money", "Rates & Policy", "Markets & Currency", "Global"]
