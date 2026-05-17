import type { ChannelMetric } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type ChannelMetricsTableProps = {
  channels: ChannelMetric[];
};

export function ChannelMetricsTable({ channels }: ChannelMetricsTableProps) {
  return (
    <section className="overviewPanel" aria-label="Channel metrics">
      <div className="sectionHeader">
        <div>
          <h2>Channel metrics</h2>
          <p>Share, growth, stability, and role</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Channel</th>
              <th>Traffic</th>
              <th>Share</th>
              <th>Growth</th>
              <th>Stability</th>
              <th>Role</th>
              <th>Hint</th>
            </tr>
          </thead>
          <tbody>
            {channels.map((channel) => (
              <tr key={channel.channel_id}>
                <td>{channel.channel_name}</td>
                <td>{formatNumber(channel.traffic)}</td>
                <td>{formatPercent(channel.traffic_share)}</td>
                <td>{formatPercent(channel.growth_rate)}</td>
                <td>{formatPercent(channel.stability_score)}</td>
                <td>
                  <span className={`pill ${channel.role}`}>{channel.role}</span>
                </td>
                <td>{channel.interpretation}</td>
              </tr>
            ))}
            {channels.length === 0 && (
              <tr>
                <td colSpan={7}>No channel data available for selected filters.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
