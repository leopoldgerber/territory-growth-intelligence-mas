import type { ChannelMetric } from '../api/client';

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type ChannelShareChartProps = {
  channels: ChannelMetric[];
};

export function ChannelShareChart({ channels }: ChannelShareChartProps) {
  return (
    <section className="overviewPanel" aria-label="Channel share">
      <div className="sectionHeader">
        <div>
          <h2>Channel share</h2>
          <p>{channels.length} channels</p>
        </div>
      </div>
      <div className="barList">
        {channels.map((channel) => (
          <div className="barRow" key={channel.channel_id}>
            <div>
              <span>{channel.channel_name}</span>
              <strong>{formatPercent(channel.traffic_share)}</strong>
            </div>
            <span className="barTrack">
              <span style={{ width: `${(channel.traffic_share ?? 0) * 100}%` }} />
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
