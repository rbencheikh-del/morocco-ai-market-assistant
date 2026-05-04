# Maroq UI Spec

This document defines a Figma-level layout specification for the Maroq AI Moroccan Stock Market Assistant MVP. The product is an analytics-only financial dashboard for Moroccan retail investors. It must feel calm, trustworthy, data-rich, and usable on desktop and mobile.

## Design Principles

- Product feel: modern fintech research terminal, not a marketing page.
- Tone: clear, concise, confidence-building, never advice-like.
- Density: information-rich but breathable; prioritize scanability over decorative layout.
- Compliance: keep `This is market analytics only, not financial advice.` visible on primary workflows.
- Interactions: all actions are review, watch, track, ask, import, or configure. Never use buy/sell as a clickable trading command.

## Frames

Desktop:

- Frame: `1440 x 1024`
- Sidebar: `280px` fixed width
- Main content: `minmax(0, 1fr)`
- Main padding: `32px`
- Section gap: `24px`
- Card radius: `8px`

Tablet:

- Frame: `834 x 1194`
- Sidebar becomes top stacked section
- Main padding: `24px`
- All two-column grids collapse to one column

Mobile:

- Frame: `390 x 844`
- Main padding: `18px`
- Cards use `18px` padding
- Tables horizontally scroll instead of compressing columns
- Sidebar nav becomes a two-column grid

## Layout Map

Desktop structure:

```text
appShell
├─ sidebar 280px
│  ├─ logo mark 44x44
│  ├─ product name + subtitle
│  ├─ nav links
│  └─ no-execution guardrail
└─ workspace
   ├─ hero
   ├─ alert bell panel
   ├─ analytics-only disclaimer
   ├─ KPI summary grid
   ├─ market brief
   ├─ ranked stocks table
   ├─ market chart + signal cards
   ├─ watchlist table
   ├─ portfolio tracker + risk alerts
   └─ AI assistant
```

## Tokens

Colors:

- Background: `#f6f8fb`
- Surface: `#ffffff`
- Soft surface: `#eef5ff`
- Text: `#142033`
- Muted text: `#607086`
- Border: `#dbe5f0`
- Primary blue: `#1266f1`
- Cyan accent: `#15b8d8`
- Positive: `#18a36b`
- Warning: `#c9860a`
- Negative: `#cf3d3d`
- Shadow: `0 20px 60px rgba(22, 37, 61, 0.1)`

Typography:

- Font stack: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- Hero H1 desktop: `clamp(2rem, 5vw, 4.4rem)`, line height `0.96`
- Section H2: `1.35rem`
- Eyebrow: `0.76rem`, `800`, uppercase, letter spacing `0`
- Body: `1rem`, line height `1.5-1.7`
- Table header: `0.78rem`, uppercase, muted

Spacing:

- Page padding desktop: `32px`
- Page padding mobile: `18px`
- Card padding desktop: `24px`
- Card padding mobile: `18px`
- Card gap: `24px`
- Compact internal gap: `8px-12px`
- Section header bottom margin: `20px`

Borders and elevation:

- Card border: `1px solid #dbe5f0`
- Card radius: `8px`
- Tool/label radius: `8px`
- Pills/badges radius: `999px`
- Standard card shadow: `0 12px 36px rgba(22, 37, 61, 0.06)`

## Components

### Sidebar

Position:

- Desktop: sticky, left, full viewport height
- Width: `280px`
- Padding: `28px`
- Gap: `24px`
- Background: `#fbfdff`
- Border right: `1px solid #dbe5f0`

Logo:

- Size: `44 x 44`
- Radius: `8px`
- Background: linear gradient from primary blue to cyan
- Text: `M`, white, `800`

Navigation:

- Links: Rankings, Market brief, Signals, Portfolio, Watchlists, Risk alerts, Ask AI
- Link padding: `10px 12px`
- Radius: `8px`
- Hover background: `#eef5ff`

Guardrail:

- Border: `#bed4ee`
- Background: `#f4f9ff`
- Copy: `No trade execution` and supporting text
- Icon: `ShieldCheck`, 18px

### Hero

Container:

- Padding: `36px`
- Border: `1px solid #dbe5f0`
- Radius: `8px`
- Background: white to soft blue with subtle cyan radial highlight
- Shadow: primary page shadow

Content:

- Eyebrow: `Casablanca Stock Exchange MVP`
- H1: `AI dashboard for Moroccan equities and manual portfolio risk.`
- Body max width: `760px`

### Alert Bell Panel

Purpose: top-right-style notification summary.

Desktop layout:

- Grid columns: `auto minmax(0, 1fr) minmax(280px, 0.9fr)`
- Padding: `16px`
- Background: white
- Bell icon box: `42 x 42`, radius `8px`, soft blue background
- Unread badge: red circle, top-right of icon, min `20px`
- Mini history: max 3 alerts

States:

- `0 unread`: hide red badge, text `0 unread research alerts`
- `1+ unread`: show count badge
- Long alert copy wraps to two lines; no layout shift

### Disclaimer Bar

Copy:

`This is market analytics only, not financial advice.`

Layout:

- Flex row
- Gap: `10px`
- Padding: `14px 16px`
- Border: `#bdd6fb`
- Background: `#f4f9ff`
- Text: primary blue

### KPI Summary Grid

Desktop:

- Four equal columns
- Gap: `12px`
- Card padding: `18px`
- Icon column: `32px`

Metrics:

- Top-ranked equities
- Research-positive signals
- High-risk stocks
- Portfolio P&L

Copy rule:

- Prefer `Research-positive signals` over `Buy signals` in final polished UI to reduce advice-like wording.

### Market Brief

Purpose: answer “what is happening today?” in one scan.

Header:

- Eyebrow: `Today’s market brief`
- H2: `Top 5 Moroccan stocks today`
- Icon: `TrendingUp`

Layout:

- Three columns desktop:
  - Top ranked
  - Biggest movers
  - Risk warnings
- Collapse to one column under `980px`

Top ranked row:

- Ticker: 56px column
- Score: 76px column
- Signal badge
- Price as small muted row

Biggest movers:

- Sort by absolute daily change
- Positive: green
- Negative: red

Risk warnings:

- Warning card background: `#fff7f7`
- Border: `#f1d3d3`
- Text: `#5a2630`
- Include explanation, not instruction

Narrative summary:

- Soft blue panel
- Label: `Simple narrative summary`
- One paragraph, max 4 sentences
- Must end or include analytics-only disclaimer

### Ranked Stocks Table

Columns:

- Rank
- Stock
- Sector
- AI score
- Signal
- Confidence
- Risk level
- Latest price
- 1M / 3M momentum
- Why

Desktop:

- `table min-width: 920px`
- Horizontal scroll wrapper
- Cell padding: `14px`

Signal badge:

- BUY: green surface, green text
- HOLD: amber surface, amber text
- SELL: red surface, red text

Preferred polished label:

- Display raw `BUY/HOLD/SELL` only as a research signal badge.
- Never style it as a primary action button.

### Chart + Signal Cards

Grid:

- Desktop: `minmax(0, 1.4fr) minmax(340px, 0.8fr)`
- Mobile: one column

Chart:

- Height: `300px`
- Transparent background
- Blue line `#1266f1`
- Ticker strip below

Signal cards:

- Grid stack gap: `12px`
- Card grid: `1fr auto`
- Include confidence, signal badge, reason, risk note

### Watchlist Table

Columns:

- Stock
- Latest price
- Signal
- Ranking score
- Daily change
- Alert levels

Behavior:

- Show first/default watchlist in dashboard.
- Watchlist detail page can later expose create/rename/delete controls.
- Alert levels show `Above` and `Below`; no order buttons.

### Portfolio Tracker

Top value block:

- Background: soft blue
- Total value large text `2rem`
- Unrealized P&L color:
  - Positive: green
  - Negative: red

Sector allocation:

- Three-column grid desktop
- Each sector card includes label, percent, meter
- Collapse to one column on mobile

Holding row:

- Grid: `minmax(0, 1fr) auto auto`
- Mobile: one column
- Include ticker, sector/note, market value, allocation, unrealized P&L

### Risk Alerts

Alert item:

- Left border communicates severity:
  - High: red
  - Medium: amber
  - Low: green
- Include severity, symbol, title/type, message, recommended review action

Copy rule:

- Use `Review`, `Watch`, `Verify`, `Monitor`.
- Avoid `Buy now`, `Sell now`, `You should`, `Recommended trade`.

### AI Assistant

Panel:

- Input + submit button
- Submit label: `Ask`
- Loading label: `Analyzing`
- Default question should be educational:
  - Good: `Compare ATW and IAM using public market metrics.`
  - Avoid: `Should I buy ATW?`

Answer:

- Include citations, tickers, disclaimer, and audit ID where available.
- Empty state explains capabilities without instructions.

## Stock Detail Page

Route:

- `/stocks/{symbol}`

Desktop layout:

```text
detailShell
├─ back link
├─ detail hero
│  ├─ company name and description
│  └─ quote card
├─ detail grid
│  ├─ signal explanation
│  ├─ company profile
│  ├─ technical indicators
│  └─ risk warnings
└─ disclaimer panel
```

Hero quote card:

- Latest price large
- Sector small muted

Signal explanation:

Use this exact structure:

```text
BUY (74% confidence)

Why:
- Strong 3M momentum
- Above 50-day trend
- Liquidity stable

Risks:
- Volatility rising
- Near resistance level

Action:
Watch for breakout above 520 MAD

Market analytics only, not financial advice.
```

If Arabic or French is selected later, keep the same block structure and translate labels.

## Responsive Rules

At `max-width: 980px`:

- App shell becomes one column
- Sidebar becomes static top section
- Two-column grids become one column
- Summary cards become one column
- Alert bell becomes one column
- Market brief becomes one column

At `max-width: 620px`:

- Sidebar padding: `20px`
- Main padding: `18px`
- Cards: `18px`
- Hero H1: `2.3rem`
- Form rows become one column
- Holding rows become one column
- Allocation, indicator, and metric grids become one column
- Tables keep horizontal scroll

## Interaction States

Buttons:

- Primary: blue background, white text, radius `8px`, height `48px`
- Disabled: opacity `0.7`, cursor wait/not-allowed
- Icon buttons: square, `40-44px`, tooltip required in final production UI

Tables:

- Row hover: soft blue background
- Links: primary blue
- Long names wrap; tickers stay bold

Loading:

- Use skeleton blocks for:
  - KPI cards
  - ranked table rows
  - chart area
  - watchlist rows

Empty states:

- Watchlist: `Create a watchlist to track Moroccan equities and analytics alerts.`
- Portfolio: `Add manual holdings to see MAD value and risk alerts.`
- Alerts: `No unread analytics alerts.`
- Market brief: `Import daily prices to generate today’s brief.`

Error states:

- Keep UI usable with fallback data.
- Show small warning: `Live API unavailable. Showing local sample data.`

## Accessibility

- Minimum contrast target: WCAG AA.
- All icon-only controls need `aria-label`.
- Alert bell panel needs `aria-label="Alert notifications"`.
- Tables need readable headers and no empty header cells.
- Signal color must be paired with text label.
- Do not rely on green/red alone for meaning.

## Implementation Checklist

- Sidebar fixed at `280px` desktop.
- Main content gap exactly `24px`.
- All cards radius `8px`.
- No nested cards except repeated row/card items.
- Tables scroll horizontally on mobile.
- Disclaimer visible above primary data sections.
- BUY/HOLD/SELL are badges only, never primary action buttons.
- Signal explanation uses the approved `Why / Risks / Action` block.
- Arabic/French copy preserves structure and does not overflow cards.
- All responsive breakpoints tested at `1440`, `834`, and `390`.

## QA Acceptance

Desktop `1440 x 1024`:

- Sidebar visible without page horizontal scroll.
- Hero, alert bell, disclaimer, KPIs, market brief, rankings all visible in order.
- Ranked table scrolls only inside table wrapper if needed.

Tablet `834 x 1194`:

- Sidebar stacks above workspace.
- Market brief columns collapse.
- Chart and signal cards stack.

Mobile `390 x 844`:

- Text does not overlap.
- Tables are horizontally scrollable.
- Alert bell badge remains visible.
- No card content overflows its container.

Compliance:

- At least one visible disclaimer on dashboard and stock detail page.
- No text says the app executes trades.
- No CTA instructs users to buy or sell.
