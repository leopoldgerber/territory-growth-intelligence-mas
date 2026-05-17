import type { OpportunityScore } from '../api/client';

function formatScore(value: number | null | undefined) {
  return value == null ? 'n/a' : value.toFixed(2);
}

type OpportunityScoreCardProps = {
  opportunity: OpportunityScore | null;
};

export function OpportunityScoreCard({ opportunity }: OpportunityScoreCardProps) {
  if (!opportunity) {
    return null;
  }

  const components: Array<[string, number | null]> = [
    ['Traffic', opportunity.components.traffic_score],
    ['Competition', opportunity.components.competition_score],
    ['Quality', opportunity.components.quality_score],
    ['Channel gap', opportunity.components.channel_gap_score],
    ['Volatility', opportunity.components.volatility_score],
    ['Localization', opportunity.components.localization_potential_score],
    ['Entry difficulty', opportunity.components.entry_difficulty_score],
  ];

  return (
    <section className="overviewPanel" aria-label="Opportunity score">
      <div className="sectionHeader">
        <div>
          <h2>Opportunity Score</h2>
          <p>Country priority and score breakdown</p>
        </div>
        <span className={`pill ${opportunity.score.recommended_priority}`}>{opportunity.score.recommended_priority}</span>
      </div>
      <div className="opportunityHero">
        <strong>{formatScore(opportunity.score.opportunity_score)}</strong>
        <div>
          <span>Market type</span>
          <b>{opportunity.score.market_type}</b>
        </div>
      </div>
      <div className="scoreBreakdown">
        {components.map(([label, value]) => (
          <div className="scoreRow" key={label}>
            <span>{label}</span>
            <strong>{formatScore(value)}</strong>
            <span className="barTrack">
              <span style={{ width: `${(value ?? 0) * 100}%` }} />
            </span>
          </div>
        ))}
      </div>
      <div className="opportunityColumns">
        <div>
          <h3>Strengths</h3>
          <ul className="hintList">
            {opportunity.strengths.map((strength) => (
              <li key={strength}>{strength}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Risks</h3>
          <ul className="hintList">
            {opportunity.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </div>
      </div>
      <p className="generatedSummary">{opportunity.explanation}</p>
      {opportunity.data_quality_status === 'warning' && (
        <p className="qualityWarning">Opportunity score is based on data with quality warnings.</p>
      )}
    </section>
  );
}
