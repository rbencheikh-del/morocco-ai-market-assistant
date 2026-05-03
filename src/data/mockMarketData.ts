import type { DummyHolding, MarketSummaryItem, PortfolioSeries, RiskAlert, RiskSimulation, WatchlistItem } from "../types/market";

export const marketSummary: MarketSummaryItem[] = [
  { label: "MASI", value: "14,928.21", detail: "+0.84%", tone: "positive" },
  { label: "MAD Liquidity", value: "342M", detail: "Normal", tone: "neutral" },
  { label: "Risk Mode", value: "Balanced", detail: "Active", tone: "positive" },
];

export const portfolioSeries: PortfolioSeries = {
  "1M": [
    { label: "W1", value: 120000 },
    { label: "W2", value: 120800 },
    { label: "W3", value: 120200 },
    { label: "W4", value: 121400 },
    { label: "W5", value: 122300 },
    { label: "W6", value: 122850 },
    { label: "W7", value: 123100 },
  ],
  "6M": [
    { label: "Jan", value: 120000 },
    { label: "Feb", value: 117800 },
    { label: "Mar", value: 119400 },
    { label: "Apr", value: 124300 },
    { label: "May", value: 127200 },
    { label: "Jun", value: 126600 },
    { label: "Jul", value: 131500 },
  ],
  "1Y": [
    { label: "Q1", value: 120000 },
    { label: "Q2", value: 116500 },
    { label: "Q3", value: 118200 },
    { label: "Q4", value: 121600 },
    { label: "Q5", value: 128000 },
    { label: "Q6", value: 132400 },
    { label: "Q7", value: 129900 },
    { label: "Q8", value: 136800 },
    { label: "Q9", value: 141200 },
  ],
};

export const watchlist: WatchlistItem[] = [
  {
    ticker: "ATW",
    name: "Attijariwafa Bank",
    sector: "Banking",
    score: 84,
    stance: "Income quality",
    signal: "Hold",
    reason: "High quality score, but bank exposure is already meaningful.",
    alert: "Watch sector concentration",
  },
  {
    ticker: "IAM",
    name: "Maroc Telecom",
    sector: "Telecom",
    score: 79,
    stance: "Dividend stability",
    signal: "Buy",
    reason: "Defensive profile and dividend stability fit balanced portfolios.",
    alert: "Confirm data freshness",
  },
  {
    ticker: "LHM",
    name: "LafargeHolcim Maroc",
    sector: "Materials",
    score: 74,
    stance: "Volume recovery",
    signal: "Sell",
    reason: "Portfolio concentration is high relative to the simulated risk profile.",
    alert: "Reduce single-name exposure",
  },
  {
    ticker: "TQM",
    name: "Taqa Morocco",
    sector: "Utilities",
    score: 71,
    stance: "Defensive cash flow",
    signal: "Hold",
    reason: "Useful defensive cash-flow exposure, but entry timing is neutral.",
    alert: "Monitor volatility",
  },
  {
    ticker: "BOA",
    name: "Bank of Africa",
    sector: "Banking",
    score: 68,
    stance: "Momentum watch",
    signal: "Hold",
    reason: "Momentum is improving, but confidence remains below top-ranked names.",
    alert: "Avoid over-adding banks",
  },
];

export const signalExplanations = [
  "Screens Casablanca-listed names by liquidity, trend quality, dividend consistency, and concentration risk.",
  "Ranks opportunities in MAD terms so retail investors can plan allocation size before placing any order.",
  "Adds plain-language rationale to keep AI output reviewable before a user acts on it.",
];

export const riskAlerts: RiskAlert[] = [
  {
    title: "Single-stock concentration",
    detail: "LHM represents 45% of the manual portfolio, above the suggested balanced profile limit.",
    severity: "high",
  },
  {
    title: "Banking sector exposure",
    detail: "ATW and BOA together create meaningful banking-sector concentration.",
    severity: "medium",
  },
  {
    title: "No execution enabled",
    detail: "Maroq tracks and explains decisions only. Users must manage any real-world orders outside the app.",
    severity: "low",
  },
];

export const dummyPortfolio: DummyHolding[] = [
  {
    ticker: "ATW",
    name: "Attijariwafa Bank",
    sector: "Banking",
    shares: 60,
    priceMad: 480,
    valueMad: 28800,
    allocation: 24,
    aiAction: "Hold",
    aiScore: 84,
  },
  {
    ticker: "IAM",
    name: "Maroc Telecom",
    sector: "Telecom",
    shares: 250,
    priceMad: 91,
    valueMad: 22750,
    allocation: 19,
    aiAction: "Buy",
    aiScore: 79,
  },
  {
    ticker: "LHM",
    name: "LafargeHolcim Maroc",
    sector: "Materials",
    shares: 30,
    priceMad: 1780,
    valueMad: 53400,
    allocation: 45,
    aiAction: "Sell",
    aiScore: 74,
  },
  {
    ticker: "TQM",
    name: "Taqa Morocco",
    sector: "Utilities",
    shares: 18,
    priceMad: 1040,
    valueMad: 18720,
    allocation: 16,
    aiAction: "Hold",
    aiScore: 71,
  },
  {
    ticker: "BOA",
    name: "Bank of Africa",
    sector: "Banking",
    shares: 120,
    priceMad: 185,
    valueMad: 22200,
    allocation: 18,
    aiAction: "Hold",
    aiScore: 68,
  },
];

export const riskSimulations: RiskSimulation[] = [
  {
    mode: "low",
    title: "Low risk",
    expectedReturn: 4.8,
    simulatedRevenueMad: 5760,
    projectedValueMad: 125760,
    maxDrawdown: -3.2,
    volatility: 5.1,
    winRate: 62,
    tradeCount: 6,
    aiSummary:
      "AI flags concentration in materials and favors dividend stability for a lower-risk manual portfolio.",
    recommendedTrades: ["Review LHM concentration", "Watch IAM for defensive exposure", "Keep a cash buffer note"],
  },
  {
    mode: "medium",
    title: "Medium risk",
    expectedReturn: 8.9,
    simulatedRevenueMad: 10680,
    projectedValueMad: 130680,
    maxDrawdown: -6.8,
    volatility: 9.4,
    winRate: 57,
    tradeCount: 12,
    aiSummary:
      "AI balances dividend names with selective momentum, while flagging single-stock exposure above 30%.",
    recommendedTrades: ["Review LHM allocation", "Keep ATW as hold", "Monitor TQM defensive exposure"],
  },
  {
    mode: "high",
    title: "High risk",
    expectedReturn: 15.4,
    simulatedRevenueMad: 18480,
    projectedValueMad: 138480,
    maxDrawdown: -13.5,
    volatility: 17.8,
    winRate: 49,
    tradeCount: 24,
    aiSummary:
      "AI allows more momentum exposure in the analysis, but flags higher drawdown risk and less reliable outcomes.",
    recommendedTrades: ["Review BOA momentum risk", "Flag LHM drawdown sensitivity", "Keep execution outside Maroq"],
  },
];
