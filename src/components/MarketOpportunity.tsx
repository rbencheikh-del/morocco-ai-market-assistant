type OpportunityMetric = {
  label: string;
  value: string;
  detail: string;
};

type OpportunityCard = {
  title: string;
  text: string;
  source: string;
};

type Props = {
  cards: OpportunityCard[];
  eyebrow: string;
  heading: string;
  metrics: OpportunityMetric[];
};

export function MarketOpportunity({ cards, eyebrow, heading, metrics }: Props) {
  return (
    <section className="opportunity-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{heading}</h2>
        </div>
      </div>

      <div className="opportunity-metrics">
        {metrics.map((metric) => (
          <article key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <p>{metric.detail}</p>
          </article>
        ))}
      </div>

      <div className="opportunity-grid">
        {cards.map((card) => (
          <article key={card.title}>
            <strong>{card.title}</strong>
            <p>{card.text}</p>
            <span>{card.source}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
