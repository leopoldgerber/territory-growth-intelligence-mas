import type { CompetitorCountryItem } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type CompetitorCountriesTableProps = {
  countries: CompetitorCountryItem[];
};

export function CompetitorCountriesTable({ countries }: CompetitorCountriesTableProps) {
  return (
    <section className="overviewPanel" aria-label="Competitor countries">
      <div className="sectionHeader">
        <div>
          <h2>Competitor countries</h2>
          <p>{countries.length} markets</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Country</th>
              <th>Region</th>
              <th>Traffic</th>
              <th>Share</th>
              <th>Growth</th>
              <th>Stability</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {countries.map((country) => (
              <tr key={country.country_id}>
                <td>{country.rank}</td>
                <td>{country.country_name_en}</td>
                <td>{country.region_name_en ?? 'n/a'}</td>
                <td>{formatNumber(country.traffic)}</td>
                <td>{formatPercent(country.traffic_share_in_domain)}</td>
                <td>{formatPercent(country.growth_rate)}</td>
                <td>{formatPercent(country.presence_stability_score)}</td>
                <td>
                  <span className={`pill ${country.quality_label}`}>{country.country_role}</span>
                </td>
              </tr>
            ))}
            {countries.length === 0 && (
              <tr>
                <td colSpan={8}>No countries for selected period.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
