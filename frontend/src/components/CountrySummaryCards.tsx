import type { CountrySummaryMetrics } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type CountrySummaryCardsProps = {
  metrics: CountrySummaryMetrics;
};

export function CountrySummaryCards({ metrics }: CountrySummaryCardsProps) {
  const cards = [
    ['Total traffic', formatNumber(metrics.total_competitor_traffic)],
    ['Active competitors', formatNumber(metrics.active_competitors_count)],
    ['Market leader', metrics.leader_company ?? metrics.leader_domain ?? 'n/a'],
    ['Top-3 share', formatPercent(metrics.top_3_share)],
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
