# Daily AI Market Brief Design

The Daily AI Market Brief is the first thing a Moroccan retail investor should read each morning. It gives a fast, explainable view of the Casablanca-listed equities universe without sounding like trade advice.

## Goal

Help users answer four questions in under 60 seconds:

- What looks strongest today?
- What moved the most?
- What risks need attention?
- What should I watch next?

The brief must remain analytics-only. It should never say "buy this" or "sell this now."

## Placement

Dashboard order:

1. Hero
2. Alert bell
3. Analytics-only disclaimer
4. KPI summary
5. Daily AI Market Brief
6. Rankings table
7. Charts and signals
8. Watchlists
9. Portfolio and risk alerts

## Desktop Layout

Frame: `1440px` width

Container:

- Full-width panel inside workspace
- Padding: `24px`
- Radius: `8px`
- Border: `1px solid #dbe5f0`
- Background: `#ffffff`
- Shadow: `0 12px 36px rgba(22, 37, 61, 0.06)`

Header:

```text
Today’s AI Market Brief
Casablanca-listed equities, refreshed from latest available market data
```

Right-side meta:

```text
Data: Mock / CSV / Live
Updated: 09:45
MAD
```

Body grid:

```text
┌─────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Market Summary              │ Top 5 Ranked Stocks          │ Biggest Movers              │
│ Narrative paragraph         │ Compact ranked list          │ Up/down move list           │
├─────────────────────────────┴─────────────────────────────┴─────────────────────────────┤
│ Risk Warnings                                                                           │
│ Three warning cards                                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ What To Watch Next                                                                       │
│ Three watch items, not trade instructions                                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

Column widths:

- Summary: `1.1fr`
- Top ranked: `1fr`
- Movers: `1fr`
- Gap: `18px`

## Mobile Layout

At `< 980px`, stack:

1. Summary
2. Top 5
3. Movers
4. Risk warnings
5. Watch next

At `< 620px`:

- Card padding: `18px`
- Lists use single-column rows
- Show only top 3 ranked stocks by default
- Add “View all ranked stocks” anchor to rankings table

## Content Blocks

### 1. Summary

Purpose: human narrative.

Example:

```text
Moroccan equities are mixed today. ATW leads the ranked list with strong liquidity and stable trend support. LHM is the biggest risk watch after a sharp daily move and elevated concentration risk. Treat this as a research brief, not financial advice.
```

Rules:

- 3 to 4 sentences max
- Mention one leader
- Mention one caution
- Mention market state: positive, mixed, cautious, thin liquidity, or defensive
- Include analytics-only wording

### 2. Top 5 Ranked Stocks

Each row:

```text
#1 ATW
Attijariwafa Bank
Score 84 / Signal HOLD / Confidence 76%
Price 480 MAD
```

Visual:

- Rank pill: blue
- Signal badge:
  - BUY / Positive: green
  - HOLD / Neutral: amber
  - SELL / Negative: red
- Score meter: 0-100

Copy rule:

- UI label should say `Research signal`, not `Recommendation`.

### 3. Biggest Movers

Each row:

```text
LHM -5.8%
Sharp daily move; verify news and data quality.
```

Sorting:

- Sort by absolute daily change
- Show top 5

Visual:

- Positive move: green
- Negative move: red
- Neutral/small move: muted

Risk copy:

- If move > 5%: `Verify news and data quality.`
- If move > 10%: `Large move; review volatility and liquidity before relying on signal.`

### 4. Risk Warnings

Show up to 3 primary warnings:

- High volatility
- Low liquidity
- Negative signal
- Risk level increase
- Price move above +/- 5%
- Missing or stale market data

Warning card:

```text
High volatility
MNG has elevated 30-day volatility.
Action: Review whether this fits your risk profile.
```

Tone:

- Use `Review`, `Verify`, `Watch`, `Monitor`
- Avoid `Act now`, `Buy`, `Sell`, `Enter`, `Exit`

### 5. What To Watch Next

This is the most product-defining part. It turns analytics into safe next steps.

Examples:

```text
Watch ATW near 500 MAD for trend confirmation.
Review LHM volatility before changing any manual portfolio assumption.
Check IAM liquidity and dividend context in the next data refresh.
```

Rules:

- Three bullets max
- Must be framed as research tasks
- No instruction to place an order
- If price level is missing, say `next resistance area` instead of inventing a number

## Empty States

No rankings:

```text
Import daily market data to generate the AI market brief.
```

No movers:

```text
Daily change data is not available yet.
```

No warnings:

```text
No major risk warnings in the latest dataset.
```

Stale data:

```text
Latest prices may be stale. Refresh market data before relying on today’s brief.
```

## Data Contract

The component can be powered by existing dashboard data:

```ts
type DailyMarketBrief = {
  asOf: string;
  dataMode: "mock" | "csv" | "live";
  summary: string;
  topRanked: Array<{
    symbol: string;
    name: string;
    score: number;
    signal: "BUY" | "HOLD" | "SELL";
    confidence: number;
    latestPriceMad?: number;
  }>;
  movers: Array<{
    symbol: string;
    dailyChangePct: number;
    note: string;
  }>;
  riskWarnings: Array<{
    alertType: string;
    severity: "Low" | "Medium" | "High";
    symbol?: string;
    message: string;
    action: string;
  }>;
  watchNext: string[];
};
```

MVP shortcut:

- Derive `topRanked` from `/rankings`
- Derive `movers` from ranking rows enriched with `daily_change_pct`
- Derive `riskWarnings` from `/alerts/unread` and risk rules
- Generate `summary` and `watchNext` deterministically from the top ranked row, biggest mover, and highest severity warning

## Visual Details

Header:

- Eyebrow: `Daily brief`
- H2: `Today’s AI Market Brief`
- Subtitle: `Casablanca-listed equities, refreshed from latest available market data`

Meta chips:

- `MAD`
- `Research only`
- `Updated 09:45`

Section titles:

- `Market Summary`
- `Top 5 Ranked`
- `Biggest Movers`
- `Risk Warnings`
- `What To Watch Next`

Microcopy:

- Use “research signal”
- Use “latest available data”
- Use “watch/review/verify”
- Avoid “recommendation”

## Acceptance Criteria

- User can understand the day in under 60 seconds.
- Top 5 stocks are visible without opening another page on desktop.
- Biggest mover and main warning are visible above the fold on desktop.
- Every warning includes a plain action.
- Disclaimer or research-only chip is visible.
- Mobile layout has no horizontal page overflow.
- No copy implies personalised financial advice.

## Future Enhancements

- French and Arabic toggle
- PDF/email export
- Scheduled morning notification
- Sector-level brief
- Data freshness banner
- Links into stock detail pages
- AI-generated summary with audit log
