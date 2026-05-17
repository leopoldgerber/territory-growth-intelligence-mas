import type { DailyTrendItem } from '../api/client';

type TrafficTrendChartProps = {
  trend: DailyTrendItem[];
};

export function TrafficTrendChart({ trend }: TrafficTrendChartProps) {
  const maxTraffic = Math.max(...trend.map((item) => item.traffic), 0);
  const points = trend
    .map((item, index) => {
      const x = trend.length <= 1 ? 0 : (index / (trend.length - 1)) * 100;
      const y = maxTraffic === 0 ? 100 : 100 - (item.traffic / maxTraffic) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <section className="overviewPanel" aria-label="Traffic trend">
      <div className="sectionHeader">
        <div>
          <h2>Traffic trend</h2>
          <p>{trend.length} days</p>
        </div>
      </div>
      <svg className="trendChart" preserveAspectRatio="none" viewBox="0 0 100 100">
        <polyline fill="none" points={points} stroke="#1c4f5f" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
      </svg>
    </section>
  );
}
