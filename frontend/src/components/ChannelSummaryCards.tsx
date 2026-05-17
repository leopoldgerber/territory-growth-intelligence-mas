import type { ChannelSummaryMetrics } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type ChannelSummaryCardsProps = {
  summary: ChannelSummaryMetrics;
};

export function ChannelSummaryCards({ summary }: ChannelSummaryCardsProps) {
  const cards = [
    ['Total channel traffic', formatNumber(summary.total_channel_traffic)],
    ['Dominant channel', summary.dominant_channel?.channel_name ?? 'n/a'],
    ['Dependency score', formatPercent(summary.channel_dependency_score)],
    ['Diversification', formatPercent(summary.channel_diversification_score)],
    ['Channel profile', summary.channel_profile],
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
