import { useCallback, useEffect, useState } from 'react';

import {
  analyzeMAS,
  getCountries,
  getCountryPeriod,
  getMASRun,
  getMASRuns,
  type CountryItem,
  type MASRunListItem,
  type MASRunResponse,
  type JobItem,
} from '../api/client';
import { CountrySelector } from '../components/CountrySelector';
import { JobProgressPanel } from '../components/JobProgressPanel';
import { PeriodSelector } from '../components/PeriodSelector';

export function StrategyAssistantPage() {
  const [countries, setCountries] = useState<CountryItem[]>([]);
  const [countryId, setCountryId] = useState<number | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [query, setQuery] = useState('Build a market entry strategy for the selected country.');
  const [budgetAmount, setBudgetAmount] = useState(10000);
  const [currencyCode, setCurrencyCode] = useState('EUR');
  const [campaignGoal, setCampaignGoal] = useState('market_test');
  const [run, setRun] = useState<MASRunResponse | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [history, setHistory] = useState<MASRunListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadCountries = useCallback(async () => {
    const countryList = await getCountries();
    setCountries(countryList.items);
    if (countryList.items.length > 0) {
      setCountryId(countryList.items[0].country_id);
    }
  }, []);

  const loadPeriod = useCallback(async (selectedCountryId: number) => {
    const period = await getCountryPeriod(selectedCountryId);
    setDateFrom(period.date_min ?? '');
    setDateTo(period.date_max ?? '');
  }, []);

  const loadHistory = useCallback(async () => {
    const runList = await getMASRuns();
    setHistory(runList.items);
  }, []);

  const startAnalysis = async () => {
    if (!countryId || dateFrom === '' || dateTo === '') {
      setError('Select country and period before running MAS analysis.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const queuedJob = await analyzeMAS({
        user_query: query,
        country_id: countryId,
        date_from: dateFrom,
        date_to: dateTo,
        budget_amount: budgetAmount > 0 ? budgetAmount : null,
        currency_code: currencyCode,
        campaign_goal: campaignGoal,
        risk_appetite: 'medium',
        calculation_version: 'v1',
      });
      setJobId(queuedJob.job_id);
      await loadHistory();
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown MAS analysis error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const finishJob = async (job: JobItem) => {
    if (job.result_payload != null) {
      setRun(job.result_payload as unknown as MASRunResponse);
    }
    await loadHistory();
    setIsLoading(false);
  };

  const openRun = async (runId: number) => {
    const savedRun = await getMASRun(runId);
    setRun(savedRun);
  };

  useEffect(() => {
    void loadCountries();
    void loadHistory();
  }, [loadCountries, loadHistory]);

  useEffect(() => {
    if (countryId) {
      void loadPeriod(countryId);
    }
  }, [countryId, loadPeriod]);

  return (
    <section className="countryOverview" aria-label="Strategy assistant">
      <div className="sectionHeader">
        <div>
          <h2>Strategy Assistant</h2>
          <p>Rule-based MAS orchestration over country, competitor, channel, opportunity, and budget tools</p>
        </div>
        {run && <span className={`pill ${run.run_status ?? ''}`}>{run.run_status}</span>}
      </div>

      <div className="assistantLayout">
        <div className="assistantMain">
          <div className="assistantForm">
            <label className="queryLabel">
              <span>Request</span>
              <textarea value={query} onChange={(event) => setQuery(event.target.value)} />
            </label>
            <CountrySelector countries={countries} countryId={countryId} onCountryChange={setCountryId} />
            <PeriodSelector
              dateFrom={dateFrom}
              dateTo={dateTo}
              dateMin={null}
              dateMax={null}
              onDateFromChange={setDateFrom}
              onDateToChange={setDateTo}
            />
            <label>
              <span>Budget</span>
              <input min="0" type="number" value={budgetAmount} onChange={(event) => setBudgetAmount(Number(event.target.value))} />
            </label>
            <label>
              <span>Currency</span>
              <input maxLength={3} value={currencyCode} onChange={(event) => setCurrencyCode(event.target.value.toUpperCase())} />
            </label>
            <label>
              <span>Goal</span>
              <select value={campaignGoal} onChange={(event) => setCampaignGoal(event.target.value)}>
                <option value="market_test">Market test</option>
                <option value="growth">Growth</option>
                <option value="aggressive_entry">Aggressive entry</option>
                <option value="brand_awareness">Brand awareness</option>
                <option value="performance">Performance</option>
              </select>
            </label>
            <button type="button" onClick={startAnalysis} disabled={isLoading}>
              {isLoading ? 'Running' : 'Run MAS'}
            </button>
          </div>

          {error !== '' && <p className="errorText">{error}</p>}
          <JobProgressPanel jobId={jobId} title="MAS progress" onComplete={(job) => void finishJob(job)} />

          {run && (
            <>
              <div className="reportPanel">
                <h3>Final Answer</h3>
                <pre className="reportMarkdown">{run.final_answer}</pre>
              </div>

              <div className="assistantColumns">
                <div className="overviewPanel">
                  <h3>Steps</h3>
                  <ol className="timelineList">
                    {run.steps.map((step) => (
                      <li key={step.agent_step_id}>
                        <strong>{step.agent_name}</strong>
                        <span className={`pill ${step.step_status ?? ''}`}>{step.step_status}</span>
                        <p>{step.summary}</p>
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="overviewPanel">
                  <h3>Recommendations</h3>
                  <ul className="hintList">
                    {run.recommendations.map((item) => (
                      <li key={item.recommendation_id}>
                        <strong>{item.title}</strong>
                        <span> {item.description}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="overviewPanel">
                <h3>Evidence</h3>
                <div className="tableScroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Source</th>
                        <th>Metric</th>
                        <th>Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {run.evidence.map((item) => (
                        <tr key={item.evidence_id}>
                          <td>{item.source_name}</td>
                          <td>{item.metric_name}</td>
                          <td>{item.metric_value ?? '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>

        <aside className="overviewPanel">
          <h3>Run History</h3>
          <div className="tableScroll">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.agent_run_id}>
                    <td>
                      <button type="button" onClick={() => void openRun(item.agent_run_id)}>
                        #{item.agent_run_id}
                      </button>
                    </td>
                    <td>
                      <span className={`pill ${item.run_status ?? ''}`}>{item.run_status}</span>
                    </td>
                    <td>{item.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </aside>
      </div>
    </section>
  );
}
