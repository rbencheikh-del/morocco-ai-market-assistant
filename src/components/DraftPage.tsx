type DraftMetric = {
  label: string;
  tone?: string;
  value: string;
};

type DraftSection = {
  title: string;
  text: string;
  items: string[];
};

type Props = {
  description: string;
  metrics: DraftMetric[];
  sectionEyebrow: string;
  sections: DraftSection[];
};

export function DraftPage({ description, metrics, sectionEyebrow, sections }: Props) {
  return (
    <section className="draft-page">
      <p className="page-intro">{description}</p>

      <div className="draft-metrics">
        {metrics.map((metric) => (
          <article key={metric.label}>
            <span>{metric.label}</span>
            <strong className={metric.tone}>{metric.value}</strong>
          </article>
        ))}
      </div>

      <div className="draft-sections">
        {sections.map((section) => (
          <article className="panel draft-card" key={section.title}>
            <div className="panel-heading">
              <div>
                <p className="eyebrow">{sectionEyebrow}</p>
                <h2>{section.title}</h2>
              </div>
            </div>
            <p>{section.text}</p>
            <div className="checklist">
              {section.items.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
