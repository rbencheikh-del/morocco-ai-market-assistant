type Pillar = {
  title: string;
  text: string;
  status: string;
};

type Props = {
  eyebrow: string;
  heading: string;
  pillars: Pillar[];
};

export function SolutionPillars({ eyebrow, heading, pillars }: Props) {
  return (
    <section className="solution-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{heading}</h2>
        </div>
      </div>
      <div className="solution-grid">
        {pillars.map((pillar) => (
          <article key={pillar.title}>
            <span>{pillar.status}</span>
            <strong>{pillar.title}</strong>
            <p>{pillar.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
