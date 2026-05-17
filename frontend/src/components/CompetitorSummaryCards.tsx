import type { CompetitorSummaryMetrics } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type CompetitorSummaryCardsProps = {
  metrics: CompetitorSummaryMetrics;
};

export function CompetitorSummaryCards({ metrics }: CompetitorSummaryCardsProps) {
  const cards = [
    ['Total traffic', formatNumber(metrics.total_traffic)],
    ['Active countries', formatNumber(metrics.active_countries_count)],
    ['Top country', metrics.top_country ?? 'n/a'],
    ['Top country share', formatPercent(metrics.top_country_share)],
    ['Desktop share', formatPercent(metrics.desktop_share)],
    ['Mobile share', formatPercent(metrics.mobile_share)],
    ['Bounce share', formatPercent(metrics.bounce_share)],
    ['No-bounce share', formatPercent(metrics.no_bounce_share)],
  ];

  return (
    <div className="metricGrid">
      {cards.map(([label, value]) => (
        <div className="metricCard" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}
