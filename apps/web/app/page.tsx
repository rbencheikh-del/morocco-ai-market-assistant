import { AssistantPanel } from "./components/AssistantPanel";
import { AlertBellPanel } from "./components/AlertBellPanel";
import { DashboardSummary } from "./components/DashboardSummary";
import { MarketChart } from "./components/MarketChart";
import { MarketBrief } from "./components/MarketBrief";
import { PortfolioTracker } from "./components/PortfolioTracker";
import { RankedStocksTable } from "./components/RankedStocksTable";
import { RiskAlerts } from "./components/RiskAlerts";
import { SignalCards } from "./components/SignalCards";
import { ShieldCheck } from "lucide-react";
import { WatchlistPage } from "./components/WatchlistPage";
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
          <a href="#brief">Market brief</a>
          <a href="#signals">Signals</a>
          <a href="#portfolio">Portfolio</a>
          <a href="#watchlists">Watchlists</a>
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

        <AlertBellPanel alerts={data.unreadAlerts} />

        <section className="disclaimerPanel" role="note">
          <ShieldCheck size={18} />
          <strong>This is market analytics only, not financial advice.</strong>
        </section>

        <DashboardSummary data={data} />

        <section id="brief">
          <MarketBrief data={data} />
        </section>

        <section id="rankings">
          <RankedStocksTable rankings={data.rankings} />
        </section>

        <section className="grid two">
          <MarketChart snapshots={data.snapshots} />
          <SignalCards signals={data.signals} />
        </section>

        <section id="watchlists">
          <WatchlistPage watchlists={data.watchlists} />
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
