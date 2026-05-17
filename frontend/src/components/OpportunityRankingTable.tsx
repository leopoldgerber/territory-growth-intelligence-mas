import type { OpportunityCountryItem } from '../api/client';

function formatScore(value: number | null | undefined) {
  return value == null ? 'n/a' : value.toFixed(2);
}

type OpportunityRankingTableProps = {
  items: OpportunityCountryItem[];
};

export function OpportunityRankingTable({ items }: OpportunityRankingTableProps) {
  return (
    <section className="overviewPanel" aria-label="Opportunity ranking">
      <div className="sectionHeader">
        <div>
          <h2>Opportunity ranking</h2>
          <p>{items.length} countries</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Country</th>
              <th>Region</th>
              <th>Score</th>
              <th>Priority</th>
              <th>Market type</th>
              <th>Traffic</th>
              <th>Competition</th>
              <th>Quality</th>
              <th>Channel gap</th>
              <th>Entry difficulty</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.country_id}>
                <td>{item.country_name_en}</td>
                <td>{item.region_name_en ?? 'n/a'}</td>
                <td>{formatScore(item.opportunity_score)}</td>
                <td>
                  <span className={`pill ${item.recommended_priority}`}>{item.recommended_priority}</span>
                </td>
                <td>{item.market_type}</td>
                <td>{formatScore(item.traffic_score)}</td>
                <td>{formatScore(item.competition_score)}</td>
                <td>{formatScore(item.quality_score)}</td>
                <td>{formatScore(item.channel_gap_score)}</td>
                <td>{formatScore(item.entry_difficulty_score)}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={10}>No opportunity scores for selected period.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
