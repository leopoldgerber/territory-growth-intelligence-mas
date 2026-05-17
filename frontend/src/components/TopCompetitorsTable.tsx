import type { TopCompetitorItem } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type TopCompetitorsTableProps = {
  competitors: TopCompetitorItem[];
};

export function TopCompetitorsTable({ competitors }: TopCompetitorsTableProps) {
  return (
    <section className="overviewPanel" aria-label="Top competitors">
      <div className="sectionHeader">
        <div>
          <h2>Top competitors</h2>
          <p>{competitors.length} domains</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Company</th>
              <th>Domain</th>
              <th>Traffic</th>
              <th>Share</th>
              <th>Desktop / Mobile</th>
              <th>Bounce</th>
              <th>No-bounce</th>
            </tr>
          </thead>
          <tbody>
            {competitors.map((competitor) => (
              <tr key={competitor.domain_id}>
                <td>{competitor.rank}</td>
                <td>{competitor.company_name ?? 'n/a'}</td>
                <td>{competitor.domain}</td>
                <td>{formatNumber(competitor.traffic)}</td>
                <td>{formatPercent(competitor.traffic_share)}</td>
                <td>
                  {formatPercent(competitor.desktop_share)} / {formatPercent(competitor.mobile_share)}
                </td>
                <td>{formatPercent(competitor.bounce_rate)}</td>
                <td>{formatNumber(competitor.traffic_no_bounce)}</td>
              </tr>
            ))}
            {competitors.length === 0 && (
              <tr>
                <td colSpan={8}>No competitors for selected period.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
