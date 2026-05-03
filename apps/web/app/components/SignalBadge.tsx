import type { Signal } from "../lib/types";

const signalClass: Record<Signal["signal"], string> = {
  BUY: "badge buy",
  HOLD: "badge hold",
  SELL: "badge sell",
};

export function SignalBadge({ signal }: { signal: Signal["signal"] }) {
  return <span className={signalClass[signal]}>{signal}</span>;
}
