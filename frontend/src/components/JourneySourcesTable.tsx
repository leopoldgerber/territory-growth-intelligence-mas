import type { JourneySourceItem } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type JourneySourcesTableProps = {
  sources: JourneySourceItem[];
};

export function JourneySourcesTable({ sources }: JourneySourcesTableProps) {
  return (
    <section className="overviewPanel" aria-label="Journey sources">
      <div className="sectionHeader">
        <div>
          <h2>Journey sources</h2>
          <p>{sources.length} sources</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Source type</th>
              <th>Traffic type</th>
              <th>Channel</th>
              <th>Traffic</th>
              <th>Share</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((source) => (
              <tr key={source.journey_source_id}>
                <td>{source.source_name ?? 'n/a'}</td>
                <td>{source.source_type ?? 'n/a'}</td>
                <td>{source.traffic_type ?? 'n/a'}</td>
                <td>{source.channel_name ?? source.channel_code ?? 'n/a'}</td>
                <td>{formatNumber(source.traffic)}</td>
                <td>{formatPercent(source.traffic_share)}</td>
              </tr>
            ))}
            {sources.length === 0 && (
              <tr>
                <td colSpan={6}>Journey source details are not available for this selection.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
