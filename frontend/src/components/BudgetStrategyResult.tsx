import type { BudgetStrategyResponse } from '../api/client';

function formatNumber(value: number | null | undefined) {
  return value == null ? 'n/a' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
}

function formatMoney(value: number, currency: string) {
  return new Intl.NumberFormat('en-US', { currency, maximumFractionDigits: 0, style: 'currency' }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type BudgetStrategyResultProps = {
  strategy: BudgetStrategyResponse | null;
};

export function BudgetStrategyResult({ strategy }: BudgetStrategyResultProps) {
  if (!strategy) {
    return null;
  }

  return (
    <section className="overviewPanel" aria-label="Budget strategy result">
      <div className="sectionHeader">
        <div>
          <h2>Strategy summary</h2>
          <p>{strategy.strategy.recommended_strategy_type}</p>
        </div>
        <span className="pill high">{formatPercent(strategy.strategy.confidence_score)}</span>
      </div>
      <p className="generatedSummary">{strategy.strategy.summary}</p>

      <div className="metricGrid">
        <div className="metricCard">
          <span>Expected traffic</span>
          <strong>{formatNumber(strategy.expected_effect.expected_traffic)}</strong>
        </div>
        <div className="metricCard">
          <span>Expected leads</span>
          <strong>{formatNumber(strategy.expected_effect.expected_leads)}</strong>
        </div>
        <div className="metricCard">
          <span>Expected clients</span>
          <strong>{formatNumber(strategy.expected_effect.expected_clients)}</strong>
        </div>
        <div className="metricCard">
          <span>Budget</span>
          <strong>{formatMoney(strategy.budget.amount, strategy.budget.currency_code)}</strong>
        </div>
      </div>

      <div className="barList">
        {strategy.allocation.map((item) => (
          <div className="barRow" key={item.channel_code}>
            <div>
              <span>{item.channel_name ?? item.channel_code}</span>
              <strong>
                {formatPercent(item.budget_share)} · {formatMoney(item.budget_amount, strategy.budget.currency_code)}
              </strong>
            </div>
            <span className="barTrack">
              <span style={{ width: `${item.budget_share * 100}%` }} />
            </span>
          </div>
        ))}
      </div>

      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Channel</th>
              <th>Budget</th>
              <th>Priority</th>
              <th>Risk</th>
              <th>Traffic</th>
              <th>Leads</th>
              <th>Clients</th>
              <th>Hypothesis</th>
            </tr>
          </thead>
          <tbody>
            {strategy.allocation.map((item) => (
              <tr key={item.channel_code}>
                <td>{item.channel_name ?? item.channel_code}</td>
                <td>{formatMoney(item.budget_amount, strategy.budget.currency_code)}</td>
                <td>
                  <span className={`pill ${item.priority}`}>{item.priority}</span>
                </td>
                <td>{item.risk_level}</td>
                <td>{formatNumber(item.expected_traffic)}</td>
                <td>{formatNumber(item.expected_leads)}</td>
                <td>{formatNumber(item.expected_clients)}</td>
                <td>{item.test_hypothesis}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="opportunityColumns">
        <div>
          <h3>Recommendations</h3>
          <ul className="hintList">
            {strategy.recommendations.map((recommendation) => (
              <li key={recommendation}>{recommendation}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Risks</h3>
          <ul className="hintList">
            {strategy.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
