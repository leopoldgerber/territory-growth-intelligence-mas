import type { CompetitorCountryItem, CompetitorSignalSet } from '../api/client';

function renderCountries(countries: CompetitorCountryItem[]) {
  if (countries.length === 0) {
    return <p className="mutedText">No signals.</p>;
  }

  return (
    <ul className="signalList">
      {countries.slice(0, 5).map((country) => (
        <li key={country.country_id}>
          <span>{country.country_name_en}</span>
          <strong>{country.signal ?? country.country_role}</strong>
        </li>
      ))}
    </ul>
  );
}

type CompetitorSignalsPanelProps = {
  signals: CompetitorSignalSet;
};

export function CompetitorSignalsPanel({ signals }: CompetitorSignalsPanelProps) {
  const groups = [
    ['Anchor countries', signals.anchor_countries],
    ['Growing countries', signals.growing_countries],
    ['Declining countries', signals.declining_countries],
    ['New markets', signals.new_market_signals],
  ] as const;

  return (
    <section className="overviewPanel" aria-label="Competitor signals">
      <div className="sectionHeader">
        <div>
          <h2>Signals</h2>
          <p>Country-level movement</p>
        </div>
      </div>
      <div className="signalsGrid">
        {groups.map(([title, countries]) => (
          <div className="signalCard" key={title}>
            <h3>{title}</h3>
            {renderCountries(countries)}
          </div>
        ))}
      </div>
    </section>
  );
}
