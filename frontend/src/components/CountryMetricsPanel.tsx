import type { CountryMetricsResponse, DailyMetricItem } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : value.toFixed(2);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

function hhiLabel(value: number | null | undefined) {
  if (value == null) {
    return 'No concentration data';
  }
  if (value < 0.15) {
    return 'Fragmented market';
  }
  if (value <= 0.25) {
    return 'Moderate concentration';
  }
  return 'High concentration';
}

function scoreLabel(value: number | null | undefined, kind: string) {
  if (value == null) {
    return `No ${kind} score`;
  }
  if (value < 0.35) {
    return `Low ${kind}`;
  }
  if (value < 0.7) {
    return `Moderate ${kind}`;
  }
  return `High ${kind}`;
}

type MetricCardProps = {
  label: string;
  value: string;
  caption: string;
};

function MetricCard({ label, value, caption }: MetricCardProps) {
  return (
    <div className="metricCard">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{caption}</small>
    </div>
  );
}

type MetricTrendChartProps = {
  items: DailyMetricItem[];
  metric: keyof DailyMetricItem;
  title: string;
};

function MetricTrendChart({ items, metric, title }: MetricTrendChartProps) {
  const values = items.map((item) => Number(item[metric] ?? 0));
  const maxValue = Math.max(...values, 0);
  const points = values
    .map((value, index) => {
      const x = values.length <= 1 ? 0 : (index / (values.length - 1)) * 100;
      const y = maxValue === 0 ? 100 : 100 - (value / maxValue) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="miniChart">
      <h3>{title}</h3>
      <svg preserveAspectRatio="none" viewBox="0 0 100 100">
        <polyline fill="none" points={points} stroke="#1c4f5f" strokeWidth="2.4" vectorEffect="non-scaling-stroke" />
      </svg>
    </div>
  );
}

type CountryMetricsPanelProps = {
  metrics: CountryMetricsResponse | null;
  dailyMetrics: DailyMetricItem[];
};

export function CountryMetricsPanel({ metrics, dailyMetrics }: CountryMetricsPanelProps) {
  if (!metrics) {
    return null;
  }

  const values = metrics.metrics;

  return (
    <section className="overviewPanel" aria-label="Country metrics">
      <div className="sectionHeader">
        <div>
          <h2>Country metrics</h2>
          <p>
            {metrics.calculation.calculation_version} / {metrics.calculation.data_quality_status ?? 'unknown'}
          </p>
        </div>
      </div>

      {metrics.warning && <div className="qualityWarning">{metrics.warning}</div>}

      <div className="metricGrid">
        <MetricCard label="Leader share" value={formatPercent(values.leader_share)} caption="Market leader dominance" />
        <MetricCard label="Top-3 share" value={formatPercent(values.top_3_share)} caption="Traffic concentration in top 3" />
        <MetricCard
          label="HHI"
          value={formatNumber(values.market_concentration_hhi)}
          caption={hhiLabel(values.market_concentration_hhi)}
        />
        <MetricCard
          label="Engagement score"
          value={formatNumber(values.engagement_score)}
          caption={scoreLabel(values.engagement_score, 'engagement')}
        />
        <MetricCard
          label="Volatility score"
          value={formatNumber(values.market_volatility_score)}
          caption={scoreLabel(values.market_volatility_score, 'volatility')}
        />
        <MetricCard
          label="Active competitors"
          value={String(values.active_competitors_count ?? 'n/a')}
          caption="Domains with traffic"
        />
        <MetricCard label="Bounce share" value={formatPercent(values.bounce_share)} caption="Lower is usually better" />
        <MetricCard label="No-bounce share" value={formatPercent(values.no_bounce_share)} caption="Higher quality traffic" />
      </div>

      <div className="metricsCharts">
        <MetricTrendChart items={dailyMetrics} metric="total_competitor_traffic" title="Daily traffic" />
        <MetricTrendChart items={dailyMetrics} metric="active_competitors_count" title="Active competitors" />
        <MetricTrendChart items={dailyMetrics} metric="leader_share" title="Leader share" />
        <MetricTrendChart items={dailyMetrics} metric="engagement_score" title="Engagement" />
      </div>
    </section>
  );
}
