import type { ChannelTrendItem } from '../api/client';

type ChannelTrendChartProps = {
  trend: ChannelTrendItem[];
};

export function ChannelTrendChart({ trend }: ChannelTrendChartProps) {
  const totals = new Map<string, number>();
  trend.forEach((item) => totals.set(item.date, (totals.get(item.date) ?? 0) + item.traffic));
  const points = Array.from(totals.entries()).sort(([firstDate], [secondDate]) => firstDate.localeCompare(secondDate));
  const maxTraffic = Math.max(...points.map(([, traffic]) => traffic), 0);
  const polyline = points
    .map(([dateValue, traffic], index) => {
      const x = points.length <= 1 ? 0 : (index / (points.length - 1)) * 100;
      const y = maxTraffic === 0 ? 100 : 100 - (traffic / maxTraffic) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <section className="overviewPanel" aria-label="Channel trend">
      <div className="sectionHeader">
        <div>
          <h2>Channel trend</h2>
          <p>{points.length} days</p>
        </div>
      </div>
      <svg className="trendChart" preserveAspectRatio="none" viewBox="0 0 100 100">
        <polyline fill="none" points={polyline} stroke="#1c4f5f" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
      </svg>
    </section>
  );
}
