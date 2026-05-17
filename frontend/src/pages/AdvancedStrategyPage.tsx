import { useEffect, useState } from 'react';

import {
  createAdvancedStrategy,
  getAdvancedScenarios,
  getCountries,
  type AdvancedStrategyRequest,
  type AdvancedStrategyResponse,
  type CountryItem,
  type GrowthScenarioList,
} from '../api/client';
import { useAuth } from '../components/AuthProvider';

function todayOffset(days: number): string {
  const dateValue = new Date();
  dateValue.setDate(dateValue.getDate() + days);
  return dateValue.toISOString().slice(0, 10);
}

function formatNumber(value: number | null | undefined): string {
  if (value == null) {
    return 'No data';
  }
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
}

function percentValue(value: number | null | undefined): string {
  if (value == null) {
    return 'No data';
  }
  return `${Math.round(value * 100)}%`;
}

export function AdvancedStrategyPage() {
  const { activeProject } = useAuth();
  const [countries, setCountries] = useState<CountryItem[]>([]);
  const [selectedCountryId, setSelectedCountryId] = useState('');
  const [budgetAmount, setBudgetAmount] = useState('30000');
  const [dateFrom, setDateFrom] = useState(todayOffset(-180));
  const [dateTo, setDateTo] = useState(todayOffset(-1));
  const [forecastStart, setForecastStart] = useState(todayOffset(1));
  const [forecastEnd, setForecastEnd] = useState(todayOffset(90));
  const [result, setResult] = useState<AdvancedStrategyResponse | null>(null);
  const [history, setHistory] = useState<GrowthScenarioList | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadOptions = async () => {
      const countryData = await getCountries();
      setCountries(countryData.items);
      if (countryData.items.length > 0) {
        setSelectedCountryId(String(countryData.items[0].country_id));
      }
    };
    void loadOptions();
  }, []);

  useEffect(() => {
    const loadHistory = async () => {
      if (activeProject == null) {
        return;
      }
      const scenarioData = await getAdvancedScenarios(activeProject.project_id);
      setHistory(scenarioData);
    };
    void loadHistory();
  }, [activeProject]);

  const runStrategy = async () => {
    if (activeProject == null || selectedCountryId === '') {
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const request: AdvancedStrategyRequest = {
        country_id: Number(selectedCountryId),
        date_from: dateFrom,
        date_to: dateTo,
        forecast_start: forecastStart,
        forecast_end: forecastEnd,
        budget_amount: Number(budgetAmount),
        currency_code: 'EUR',
        campaign_goal: 'growth',
        risk_appetite: 'medium',
        scenario_mode: 'all',
        assumptions: null,
        calculation_version: 'v2',
      };
      const strategy = await createAdvancedStrategy(activeProject.project_id, request);
      setResult(strategy);
      setHistory(await getAdvancedScenarios(activeProject.project_id));
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Advanced strategy failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="countryOverview" aria-label="Advanced strategy">
      <div className="sectionHeader">
        <div>
          <h2>Advanced Strategy</h2>
          <p>Conservative, base, and aggressive growth scenarios with CAC, ROI, payback, and tactical allocation.</p>
        </div>
        <button className="primaryButton" type="button" onClick={runStrategy} disabled={isLoading || activeProject == null}>
          Calculate
        </button>
      </div>

      <article className="workspacePanel">
        <div className="formGrid">
          <label>
            Country
            <select value={selectedCountryId} onChange={(event) => setSelectedCountryId(event.target.value)}>
              {countries.map((country) => (
                <option key={country.country_id} value={country.country_id}>
                  {country.country_name_en}
                </option>
              ))}
            </select>
          </label>
          <label>
            Period from
            <input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          </label>
          <label>
            Period to
            <input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          </label>
          <label>
            Forecast from
            <input type="date" value={forecastStart} onChange={(event) => setForecastStart(event.target.value)} />
          </label>
          <label>
            Forecast to
            <input type="date" value={forecastEnd} onChange={(event) => setForecastEnd(event.target.value)} />
          </label>
          <label>
            Budget
            <input type="number" min="1" value={budgetAmount} onChange={(event) => setBudgetAmount(event.target.value)} />
          </label>
        </div>
      </article>

      {error !== '' && <p className="errorText">{error}</p>}
      {isLoading && <p className="mutedText">Calculating advanced scenarios...</p>}

      {result != null && (
        <>
          <div className="summaryGrid">
            <article className="overviewPanel">
              <h3>Strategic Priority</h3>
              <p className="metricValue">{percentValue(result.advanced_scores.strategic_priority_score)}</p>
              <p className="mutedText">{result.recommended_strategy_type}</p>
            </article>
            <article className="overviewPanel">
              <h3>ROI Potential</h3>
              <p className="metricValue">{percentValue(result.advanced_scores.roi_potential_score)}</p>
              <p className="mutedText">Audience fit: {percentValue(result.advanced_scores.audience_fit_score)}</p>
            </article>
            <article className="overviewPanel">
              <h3>Competitor Threat</h3>
              <p className="metricValue">{percentValue(result.advanced_scores.competitor_threat_score)}</p>
              <p className="mutedText">Market maturity: {percentValue(result.advanced_scores.market_maturity_score)}</p>
            </article>
            <article className="overviewPanel">
              <h3>Paid Dependency</h3>
              <p className="metricValue">{percentValue(result.advanced_scores.paid_dependency_score)}</p>
              <p className="mutedText">SEO: {percentValue(result.advanced_scores.seo_opportunity_score)}</p>
            </article>
          </div>

          <article className="workspacePanel">
            <h3>Scenario Comparison</h3>
            <table className="dataTable">
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Traffic</th>
                  <th>Leads</th>
                  <th>Clients</th>
                  <th>Revenue</th>
                  <th>CAC</th>
                  <th>ROI</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {result.scenarios.map((scenario) => (
                  <tr key={scenario.scenario_name}>
                    <td>{scenario.scenario_name}</td>
                    <td>{formatNumber(scenario.expected_traffic_capture)}</td>
                    <td>{formatNumber(scenario.expected_leads)}</td>
                    <td>{formatNumber(scenario.expected_clients)}</td>
                    <td>{formatNumber(scenario.expected_revenue)}</td>
                    <td>{formatNumber(scenario.estimated_cac)}</td>
                    <td>{formatNumber(scenario.estimated_roi)}</td>
                    <td>{percentValue(scenario.confidence_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <article className="workspacePanel">
            <h3>Advanced Budget Allocation</h3>
            <table className="dataTable">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Share</th>
                  <th>Budget</th>
                  <th>Risk</th>
                  <th>Success metric</th>
                </tr>
              </thead>
              <tbody>
                {result.recommended_allocation.map((item) => (
                  <tr key={item.allocation_category}>
                    <td>{item.allocation_category}</td>
                    <td>{percentValue(item.budget_share)}</td>
                    <td>{formatNumber(item.budget_amount)}</td>
                    <td>{item.risk_level}</td>
                    <td>{item.success_metric}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <div className="splitLayout">
            <article className="workspacePanel">
              <h3>Risks</h3>
              {(result.risks.length === 0 ? ['No major scenario risks detected.'] : result.risks).map((risk) => (
                <p key={risk} className="mutedText">{risk}</p>
              ))}
            </article>
            <article className="workspacePanel">
              <h3>Assumptions</h3>
              <p className="mutedText">Visit to lead: {percentValue(result.assumptions.visit_to_lead_rate)}</p>
              <p className="mutedText">Lead to client: {percentValue(result.assumptions.lead_to_client_rate)}</p>
              <p className="mutedText">Gross margin: {percentValue(result.assumptions.gross_margin)}</p>
            </article>
          </div>
        </>
      )}

      <article className="workspacePanel">
        <h3>Saved Scenarios</h3>
        <p className="mutedText">{history?.total ?? 0} saved scenario rows.</p>
      </article>
    </section>
  );
}
