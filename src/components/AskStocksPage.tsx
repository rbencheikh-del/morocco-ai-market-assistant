import { RefreshCw, Send } from "lucide-react";
import { useMemo, useState } from "react";

type AskLabels = {
  answerTitle: string;
  disclaimer: string;
  emptyHint: string;
  examples: string[];
  inputLabel: string;
  orbitCenter: string;
  orbitSubcopy: string;
  placeholder: string;
  send: string;
  stages: string[];
  subtitle: string;
  tickerLabel: string;
};

type Props = {
  labels: AskLabels;
};

const knownTickers = ["ATW", "IAM", "LHM", "TQM", "BOA", "MNG", "BCP", "AKT"];

function extractTickers(question: string) {
  const normalized = question.toUpperCase();
  return knownTickers.filter((ticker) => normalized.includes(ticker));
}

export function AskStocksPage({ labels }: Props) {
  const [question, setQuestion] = useState("Should I add ATW or IAM to a balanced paper portfolio?");
  const [submittedQuestion, setSubmittedQuestion] = useState(question);
  const tickers = useMemo(() => extractTickers(submittedQuestion), [submittedQuestion]);
  const collectedTickers = tickers.length > 0 ? tickers.join(", ") : "ATW, IAM, LHM, TQM, BOA";

  function submitQuestion() {
    const trimmed = question.trim();
    setSubmittedQuestion(trimmed.length > 0 ? trimmed : labels.emptyHint);
  }

  return (
    <section className="ask-page">
      <div className="ask-shell">
        <div className="ask-copy">
          <p className="page-intro">{labels.subtitle}</p>
          <div className="ask-examples">
            {labels.examples.map((example) => (
              <button key={example} type="button" onClick={() => setQuestion(example)}>
                {example}
              </button>
            ))}
          </div>
          <div className="ask-input-card">
            <label htmlFor="stockQuestion">{labels.inputLabel}</label>
            <textarea
              id="stockQuestion"
              rows={4}
              value={question}
              placeholder={labels.placeholder}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <button className="primary-button ask-submit" type="button" onClick={submitQuestion}>
              <Send size={17} />
              {labels.send}
            </button>
          </div>
        </div>

        <div className="analysis-orbit" aria-label={labels.orbitCenter}>
          <div className="orbit-center">
            <RefreshCw size={22} />
            <span>{labels.orbitCenter}</span>
            <strong>{labels.tickerLabel}: {collectedTickers}</strong>
            <small>{labels.orbitSubcopy}</small>
          </div>
          {labels.stages.map((stage, index) => (
            <span className={`orbit-tag orbit-tag-${index + 1}`} key={stage}>
              {stage}
            </span>
          ))}
        </div>
      </div>

      <div className="ai-answer-panel">
        <div>
          <p className="eyebrow">{labels.answerTitle}</p>
          <h2>{submittedQuestion}</h2>
        </div>
        <div className="answer-grid">
          <article>
            <strong>ATW</strong>
            <p>Balanced profile fit. Stronger quality score, but position sizing should avoid bank-sector concentration.</p>
          </article>
          <article>
            <strong>IAM</strong>
            <p>Defensive dividend profile. Useful for lower volatility exposure, but growth assumptions should stay conservative.</p>
          </article>
          <article>
            <strong>Portfolio note</strong>
            <p>Simulate both in MAD first, compare drawdown impact, and keep a cash buffer before any real-world decision.</p>
          </article>
        </div>
        <p className="answer-disclaimer">{labels.disclaimer}</p>
      </div>
    </section>
  );
}
