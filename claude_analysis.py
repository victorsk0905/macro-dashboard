"""
Claude analysis layer for the Macro Dashboard Agent.

Takes the fetched indicator records, builds a compact data table, and asks
Claude to write a sharp, plain-English weekly narrative. Returns structured
sections that macro_agent.py drops into the Word summary.

Requires:  export ANTHROPIC_API_KEY="sk-ant-..."
If the key is missing or the call fails, the agent silently falls back to the
built-in rule-based summary, so scheduled runs never break.
"""

import os

# Sonnet is the right default here: strong reasoning, low cost, light task.
# Pinned-snapshot IDs are also valid; the alias tracks the latest 4.6 build.
MODEL = os.environ.get("MACRO_CLAUDE_MODEL", "claude-sonnet-4-6")

SYSTEM_PROMPT = """You are a macro strategist writing a weekly briefing for a \
sophisticated reader (former corporate lawyer, now an entrepreneur and investor) \
who wants signal, not hedging. House style:
- Bottom line first. Lead with the single most important takeaway.
- Concrete numbers over adjectives. Name the indicator and the figure.
- Plain English: a smart non-economist must understand every sentence.
- Note what CHANGED and why it matters, not just static levels.
- Flag the one or two things genuinely worth watching next.
- No filler, no throat-clearing, no restating the question.
- Never give investment advice or tell the reader to buy/sell anything. \
Describe conditions; do not recommend trades.

You will receive a table of macro indicators with latest values, prior values, \
and the direction each moved. Return your answer as strict JSON with exactly \
these keys and no others:
{
  "headline": "one punchy sentence — the week's bottom line",
  "narrative": "2-3 tight paragraphs of analysis in plain English",
  "watch": ["short bullet", "short bullet", "short bullet"],
  "regime": "one of: Expansion / Slowing / Stress / Mixed — plus 4-6 words of why"
}
Return ONLY the JSON object. No markdown fences, no preamble."""


def _build_data_block(records, fmt):
    """Compact, token-cheap table for the model."""
    lines = ["GROUP | INDICATOR | LATEST | PRIOR | DIRECTION | AS_OF"]
    for r in records:
        ind = r["ind"]
        chg = r["chg"]
        direction = "flat" if abs(chg) < 1e-9 else ("up" if chg > 0 else "down")
        lines.append(
            f"{ind['group']} | {ind['label']} | "
            f"{fmt(r['latest'], ind['unit'])} | {fmt(r['prior'], ind['unit'])} | "
            f"{direction} | {r['latest_date'].isoformat()}"
        )
    return "\n".join(lines)


def generate_analysis(records, fmt, today):
    """Return a dict with headline/narrative/watch/regime, or None if unavailable."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        print("  (no ANTHROPIC_API_KEY set — skipping Claude analysis, using rule-based summary)")
        return None

    try:
        import anthropic
    except ImportError:
        print("  (anthropic SDK not installed — run: pip install anthropic)")
        return None

    data_block = _build_data_block(records, fmt)
    user_msg = (
        f"Date: {today}\n\n"
        f"This week's macro dashboard (all data from FRED):\n\n{data_block}\n\n"
        "Write the weekly briefing as specified."
    )

    try:
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
        return _parse_json(text)
    except Exception as e:
        print(f"  (Claude analysis failed: {e} — using rule-based summary)")
        return None


def _parse_json(text):
    import json
    # strip accidental code fences
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    text = text.strip().strip("`").strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # last resort: grab the outermost { ... }
        s, e = text.find("{"), text.rfind("}")
        if s == -1 or e == -1:
            return None
        obj = json.loads(text[s:e + 1])
    # validate shape
    for k in ("headline", "narrative", "watch", "regime"):
        if k not in obj:
            return None
    if not isinstance(obj["watch"], list):
        obj["watch"] = [str(obj["watch"])]
    return obj
