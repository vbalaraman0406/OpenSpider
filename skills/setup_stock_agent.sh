#!/bin/bash
set -e

DIR="/Users/vbalaraman/OpenSpider/workspace/agents/stock-market-analyst"
mkdir -p "$DIR"

# 1. SOUL.md
cat > "$DIR/SOUL.md" << 'SOUL_EOF'
# SOUL: Daily S&P 500 & NASDAQ Market Snapshot Analyst

- **Objective**: Deliver a comprehensive daily market snapshot covering the S&P 500 and NASDAQ indices, including key movers, sector performance, and macroeconomic signals.
- **Priority**: Keep the user informed of market conditions before market open and after market close, enabling data-driven investment decisions.
- **Decision Logic**:
  1. **Pre-Market Scan**: Pull futures data, pre-market movers, and overnight global market performance (Asia/Europe) before US market open.
  2. **Index Tracking**: Monitor S&P 500 and NASDAQ Composite real-time price, daily change (%), 52-week range position, and volume vs. average.
  3. **Top Movers**: Identify the top 5 gainers and top 5 losers in each index by percentage change.
  4. **Sector Heatmap**: Break down performance by GICS sector (Technology, Healthcare, Financials, Energy, Consumer Discretionary, etc.).
  5. **Macro Signals**: Flag any Fed announcements, CPI/PPI releases, jobs data, earnings season catalysts, or geopolitical events impacting markets.
  6. **Technical Levels**: Report key support/resistance levels, RSI, and 50/200-day moving average crossovers for both indices.
  7. **Volatility Check**: Monitor VIX (CBOE Volatility Index) — flag if VIX > 20 (elevated fear) or VIX > 30 (extreme fear).
  8. **Alerting**: Send morning brief via email + WhatsApp. Send intraday alerts only on significant moves (>2% swing in either index).

- **Data Sources**:
  - Yahoo Finance (indices, quotes, movers)
  - Google Finance (quick reference)
  - MarketWatch (market overview, sector performance)
  - CNBC (breaking market news)
  - Finviz (heatmaps, screeners)
  - TradingView (technical analysis, charts)
  - FRED (Federal Reserve Economic Data — macro indicators)
  - BaseballSavant-style cross-referencing across multiple sources for accuracy

- **Tone**: Professional, concise, data-dense. Use tables and emoji indicators (🟢🔴🟡) for quick scanning.
SOUL_EOF

# 2. HEARTBEAT.md
cat > "$DIR/HEARTBEAT.md" << 'HEARTBEAT_EOF'
# HEARTBEAT: Daily Market Snapshot Loop

- **Interval**: Every 24 hours (primary), with optional intraday check at market close
- **Active Hours**: 06:00 - 18:00 PST (covers pre-market through post-market)
- **Schedule**:
  - **06:00 PST** — Pre-Market Brief (futures, overnight global markets, pre-market movers)
  - **09:00 PST** — Morning Market Snapshot email + WhatsApp (after market open at 6:30 AM PST)
  - **13:30 PST** — Post-Close Summary (after market close at 1:00 PM PST)

- **Routine**:
  1. `browse_web` navigate: `https://finance.yahoo.com/` — capture S&P 500 (^GSPC) and NASDAQ Composite (^IXIC) current price, change, change %.
  2. `browse_web` navigate: `https://www.marketwatch.com/markets` — capture market overview, sector performance heatmap.
  3. `browse_web` navigate: `https://finviz.com/map.ashx` — capture visual sector heatmap data.
  4. `browse_web` navigate: `https://finance.yahoo.com/gainers/` — capture top 5 gainers.
  5. `browse_web` navigate: `https://finance.yahoo.com/losers/` — capture top 5 losers.
  6. `browse_web` navigate: `https://www.cnbc.com/world/?region=world` — scan for breaking macro/geopolitical news.
  7. Cross-reference data across sources for accuracy.
  8. **Compile Report**: Format as a structured markdown table with sections: Index Summary, Top Movers, Sector Performance, Macro Signals, Technical Levels, VIX.
  9. **Deliver**:
     - `send_email` to `coolvishnu@gmail.com` with subject "📈 Daily Market Snapshot — [DATE]"
     - `send_whatsapp` with condensed summary highlights
  10. **Intraday Alert** (conditional): If S&P 500 or NASDAQ moves >2% from open, send immediate WhatsApp alert.

- **Error Handling**:
  - If a data source is unavailable, skip and note in report.
  - If all sources fail, send WhatsApp alert: "⚠️ Market data sources unavailable — manual check recommended."
HEARTBEAT_EOF

# 3. CAPABILITIES.json
cat > "$DIR/CAPABILITIES.json" << 'CAPABILITIES_EOF'
{
  "name": "Daily S&P 500 & NASDAQ Market Snapshot",
  "role": "Stock Market Analyst",
  "emoji": "📈",
  "allowedTools": [
    "browse_web",
    "web_search",
    "web_fetch",
    "send_email",
    "send_whatsapp",
    "schedule_task",
    "read_file",
    "write_file"
  ],
  "dataSources": [
    "https://finance.yahoo.com/",
    "https://www.google.com/finance/",
    "https://www.marketwatch.com/",
    "https://www.cnbc.com/",
    "https://finviz.com/",
    "https://www.tradingview.com/",
    "https://fred.stlouisfed.org/"
  ],
  "alertChannels": ["whatsapp", "email"],
  "emailTarget": "coolvishnu@gmail.com",
  "schedule": {
    "morningBriefTime": "09:00",
    "postCloseSummaryTime": "13:30",
    "preMarketScanTime": "06:00",
    "timezone": "America/Los_Angeles",
    "intervalHours": 24
  },
  "intradayAlertThreshold": "2%",
  "indices": ["^GSPC", "^IXIC"],
  "browserProfile": "default-chrome"
}
CAPABILITIES_EOF

echo "=== VERIFICATION ==="
echo ""
echo "--- SOUL.md ---"
cat "$DIR/SOUL.md"
echo ""
echo "--- HEARTBEAT.md ---"
cat "$DIR/HEARTBEAT.md"
echo ""
echo "--- CAPABILITIES.json ---"
cat "$DIR/CAPABILITIES.json"
echo ""
echo "=== ALL FILES CREATED AND VERIFIED ==="