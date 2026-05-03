import { BrainCircuit } from "lucide-react";
import type { Signal } from "../lib/types";
import { SignalBadge } from "./SignalBadge";

export function SignalCards({ signals }: { signals: Signal[] }) {
  return (
    <article className="panel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Signal engine</p>
          <h2>Explainable AI signals</h2>
        </div>
        <BrainCircuit size={22} />
      </div>
      <div className="signalStack">
        {signals.map((signal) => (
          <section className="signalCard" key={signal.ticker}>
            <div>
              <strong>{signal.ticker}</strong>
              <span>Confidence score {signal.confidence}%</span>
            </div>
            <SignalBadge signal={signal.signal} />
            <p>{signal.reason}</p>
            <small>{signal.risk_note}</small>
          </section>
        ))}
      </div>
    </article>
  );
}
