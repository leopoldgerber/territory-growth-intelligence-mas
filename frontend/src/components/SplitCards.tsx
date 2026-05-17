type SplitCardProps = {
  title: string;
  firstLabel: string;
  firstValue: number | null;
  secondLabel: string;
  secondValue: number | null;
};

function formatPercent(value: number | null) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

export function SplitCard({ title, firstLabel, firstValue, secondLabel, secondValue }: SplitCardProps) {
  const firstWidth = `${Math.max(0, Math.min(100, (firstValue ?? 0) * 100))}%`;

  return (
    <section className="overviewPanel splitPanel" aria-label={title}>
      <h2>{title}</h2>
      <div className="splitBar">
        <span style={{ width: firstWidth }} />
      </div>
      <div className="splitLegend">
        <p>
          <strong>{firstLabel}</strong>
          {formatPercent(firstValue)}
        </p>
        <p>
          <strong>{secondLabel}</strong>
          {formatPercent(secondValue)}
        </p>
      </div>
    </section>
  );
}
