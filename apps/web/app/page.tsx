import { AssistantPanel } from "./components/AssistantPanel";
import { DashboardSummary } from "./components/DashboardSummary";
import { MarketChart } from "./components/MarketChart";
import { PortfolioTracker } from "./components/PortfolioTracker";
import { RankedStocksTable } from "./components/RankedStocksTable";
import { RiskAlerts } from "./components/RiskAlerts";
import { SignalCards } from "./components/SignalCards";
import { ShieldCheck } from "lucide-react";
import { getDashboardData } from "./lib/api";

export default async function DashboardPage() {
  const data = await getDashboardData();

  return (
    <main className="appShell">
      <aside className="sidebar">
        <div className="brandMark">M</div>
        <div>
          <strong>Morocco AI Market Assistant</strong>
          <span>AI stock market assistant</span>
        </div>
        <nav>
          <a href="#rankings">Rankings</a>
          <a href="#signals">Signals</a>
          <a href="#portfolio">Portfolio</a>
          <a href="#alerts">Risk alerts</a>
          <a href="#assistant">Ask AI</a>
        </nav>
        <section className="guardrail">
          <ShieldCheck size={18} />
          <strong>No trade execution</strong>
          <p>This MVP ranks, explains, tracks, and alerts. Users cannot place orders.</p>
        </section>
      </aside>

      <section className="workspace">
        <header className="hero">
          <div>
            <p className="eyebrow">Casablanca Stock Exchange MVP</p>
            <h1>AI dashboard for Moroccan equities and manual portfolio risk.</h1>
            <p>
              View top-ranked Moroccan equities, buy/hold/sell signals, confidence scores, risk levels,
              and MAD-denominated portfolio performance in one focused workspace.
            </p>
          </div>
        </header>

        <DashboardSummary data={data} />

        <section id="rankings">
          <RankedStocksTable rankings={data.rankings} />
        </section>

        <section className="grid two">
          <MarketChart snapshots={data.snapshots} />
          <SignalCards signals={data.signals} />
        </section>

        <section className="grid two">
          <div id="portfolio">
            <PortfolioTracker portfolio={data.portfolio} />
          </div>
          <div id="alerts">
            <RiskAlerts alerts={data.alerts} />
          </div>
        </section>

        <section id="assistant">
          <AssistantPanel />
        </section>
      </section>
    </main>
  );
}
