"use client";

import { SendHorizonal, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { askAssistant } from "../lib/api";
import type { AskResponse } from "../lib/types";

export function AssistantPanel() {
  const [question, setQuestion] = useState("Should I watch ATW or IAM for a balanced portfolio?");
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) {
      return;
    }
    setIsLoading(true);
    try {
      setResponse(await askAssistant(question));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <article className="panel assistantPanel">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">AI assistant</p>
          <h2>Ask questions about Moroccan stocks</h2>
        </div>
        <Sparkles size={22} />
      </div>
      <form onSubmit={handleSubmit} className="askForm">
        <label htmlFor="question">Question</label>
        <div>
          <input
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about ATW, IAM, BOA, LHM..."
          />
          <button type="submit" disabled={isLoading}>
            <SendHorizonal size={18} />
            {isLoading ? "Analyzing" : "Ask"}
          </button>
        </div>
      </form>
      {response ? (
        <section className="assistantAnswer">
          <p>{response.answer}</p>
          <div>
            {response.tickers.map((ticker) => (
              <span className="pill" key={ticker}>{ticker}</span>
            ))}
          </div>
          <small>{response.disclaimer}</small>
        </section>
      ) : (
        <section className="assistantAnswer muted">
          <p>Answers include cited local data sources, audit IDs, signal explanations, and compliance disclaimers.</p>
        </section>
      )}
    </article>
  );
}
