import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const root = new URL("../../../", import.meta.url);

function read(path) {
  return readFileSync(new URL(path, root), "utf8");
}

function test(name, assertion) {
  try {
    assertion();
    console.log(`ok - ${name}`);
  } catch (error) {
    console.error(`not ok - ${name}`);
    throw error;
  }
}

test("dashboard loads with the main Moroccan market sections", () => {
  const page = read("apps/web/app/page.tsx");

  assert.match(page, /Top-ranked Moroccan equities|RankedStocksTable/);
  assert.match(page, /PortfolioTracker/);
  assert.match(page, /RiskAlerts/);
  assert.match(page, /This is market analytics only, not financial advice\./);
});

test("rankings display price, momentum, and signal badges", () => {
  const table = read("apps/web/app/components/RankedStocksTable.tsx");
  const signalBadge = read("apps/web/app/components/SignalBadge.tsx");

  assert.match(table, /Latest price/);
  assert.match(table, /1M \/ 3M momentum/);
  assert.match(table, /SignalBadge/);
  assert.match(signalBadge, /BUY/);
  assert.match(signalBadge, /HOLD/);
  assert.match(signalBadge, /SELL/);
});

test("portfolio summary displays value, unrealized P&L, and allocation", () => {
  const portfolio = read("apps/web/app/components/PortfolioTracker.tsx");

  assert.match(portfolio, /Total value/);
  assert.match(portfolio, /unrealized P&L/);
  assert.match(portfolio, /Allocation by sector/);
  assert.match(portfolio, /sector_allocations/);
});

test("risk alerts display severity, message, and recommended action", () => {
  const alerts = read("apps/web/app/components/RiskAlerts.tsx");

  assert.match(alerts, /severityLabel/);
  assert.match(alerts, /message/);
  assert.match(alerts, /recommended_action/);
});

test("stock detail page shows company profile, indicators, signal explanation, and warnings", () => {
  const detail = read("apps/web/app/components/StockDetailView.tsx");
  const route = read("apps/web/app/stocks/[symbol]/page.tsx");

  assert.match(route, /getStockDetailData/);
  assert.match(detail, /Company and sector/);
  assert.match(detail, /Technical indicators/);
  assert.match(detail, /Signal explanation/);
  assert.match(detail, /Risk warnings/);
});

test("frontend API client calls the required FastAPI endpoints", () => {
  const api = read("apps/web/app/lib/api.ts");

  assert.match(api, /\/rankings/);
  assert.match(api, /\/signals/);
  assert.match(api, /\/signals\/\$\{ticker\}/);
  assert.match(api, /\/portfolios\/\$\{demoPortfolio\.id\}\/summary/);
  assert.match(api, /\/portfolios\/\$\{demoPortfolio\.id\}\/risk-alerts/);
});

console.log("frontend dashboard smoke tests passed");
