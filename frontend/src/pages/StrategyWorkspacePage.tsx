import { useCallback, useEffect, useState } from 'react';

import {
  getRecentWorkflows,
  getWorkflowOptions,
  getWorkflowRun,
  runProjectStrategyWorkflow,
  runStrategyWorkflow,
  type WorkflowOptions,
  type WorkflowResponse,
  type WorkflowRunItem,
  type JobItem,
} from '../api/client';
import { JobProgressPanel } from '../components/JobProgressPanel';
import { useAuth } from '../components/AuthProvider';

function numberText(value: number | null): string {
  if (value == null) {
    return '-';
  }
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
}

export function StrategyWorkspacePage() {
  const { activeProject } = useAuth();
  const [options, setOptions] = useState<WorkflowOptions | null>(null);
  const [recentRuns, setRecentRuns] = useState<WorkflowRunItem[]>([]);
  const [result, setResult] = useState<WorkflowResponse | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [countryId, setCountryId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [budgetAmount, setBudgetAmount] = useState('');
  const [currencyCode, setCurrencyCode] = useState('EUR');
  const [campaignGoal, setCampaignGoal] = useState('market_test');
  const [riskAppetite, setRiskAppetite] = useState('medium');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadWorkspace = useCallback(async () => {
    setError('');
    try {
      const [optionData, workflowData] = await Promise.all([getWorkflowOptions(), getRecentWorkflows()]);
      setOptions(optionData);
      setRecentRuns(workflowData.items);
      if (optionData.countries.length > 0 && countryId === '') {
        setCountryId(String(optionData.countries[0].country_id));
      }
      if (optionData.currencies.length > 0) {
        setCurrencyCode(optionData.currencies[0]);
      }
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown workflow options error';
      setError(message);
    }
  }, [countryId]);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  const runAnalysis = async () => {
    if (countryId === '' || dateFrom === '' || dateTo === '') {
      setError('Select country and period before running analysis.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const request = {
        project_id: activeProject?.project_id ?? null,
        country_id: Number(countryId),
        date_from: dateFrom,
        date_to: dateTo,
        budget_amount: budgetAmount === '' ? null : Number(budgetAmount),
        currency_code: currencyCode,
        campaign_goal: campaignGoal,
        risk_appetite: riskAppetite,
        user_query: null,
        save_result: true,
        calculation_version: 'v1',
      };
      const queuedJob = activeProject == null
        ? await runStrategyWorkflow(request)
        : await runProjectStrategyWorkflow(activeProject.project_id, request);
      setJobId(queuedJob.job_id);
      await loadWorkspace();
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown workflow error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const finishJob = async (job: JobItem) => {
    if (job.result_payload != null) {
      setResult(job.result_payload as unknown as WorkflowResponse);
    }
    await loadWorkspace();
    setIsLoading(false);
  };

  const openRun = async (workflowRunId: number) => {
    setError('');
    try {
      const workflow = await getWorkflowRun(workflowRunId);
      if (workflow.result_payload) {
        setResult(workflow.result_payload);
      }
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown workflow history error';
      setError(message);
    }
  };

  return (
    <section className="strategyWorkspace" aria-label="Strategy workspace">
      <div className="sectionHeader">
        <div>
          <h2>Strategy Workspace</h2>
          <p>
            Run the complete country-to-strategy workflow
            {activeProject == null ? '.' : ` for ${activeProject.project_name}.`}
          </p>
        </div>
        <span className="pill quality-passed">{options?.latest_data_quality_status || 'unknown'}</span>
      </div>

      <div className="workspaceGrid">
        <div className="workspacePanel">
          <h3>Analysis setup</h3>
          <div className="strategyForm">
            <label>
              Country
              <select value={countryId} onChange={(event) => setCountryId(event.target.value)}>
                {options?.countries.map((country) => (
                  <option key={country.country_id} value={country.country_id}>
                    {country.country_name_en}
                  </option>
                ))}
              </select>
            </label>
            <label>
              From
              <input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
            </label>
            <label>
              To
              <input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
            </label>
            <label>
              Budget
              <input value={budgetAmount} onChange={(event) => setBudgetAmount(event.target.value)} placeholder="Optional" />
            </label>
            <label>
              Currency
              <select value={currencyCode} onChange={(event) => setCurrencyCode(event.target.value)}>
                {options?.currencies.map((currency) => (
                  <option key={currency} value={currency}>
                    {currency}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Campaign goal
              <select value={campaignGoal} onChange={(event) => setCampaignGoal(event.target.value)}>
                {options?.campaign_goals.map((goal) => (
                  <option key={goal} value={goal}>
                    {goal}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Risk appetite
              <select value={riskAppetite} onChange={(event) => setRiskAppetite(event.target.value)}>
                {options?.risk_appetites.map((risk) => (
                  <option key={risk} value={risk}>
                    {risk}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button className="primaryButton" type="button" onClick={runAnalysis} disabled={isLoading}>
            {isLoading ? 'Running analysis...' : 'Run analysis'}
          </button>
          {error && <p className="errorText">{error}</p>}
        </div>

        <div className="workspacePanel">
          <h3>Recent workflow runs</h3>
          <div className="compactList">
            {recentRuns.map((run) => (
              <button key={run.workflow_run_id} className="historyButton" type="button" onClick={() => void openRun(run.workflow_run_id)}>
                <strong>{run.country_name_en || 'Selected country'}</strong>
                <span>
                  {run.status} · {run.period_start || '-'} to {run.period_end || '-'}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <JobProgressPanel jobId={jobId} title="Strategy workflow progress" onComplete={(job) => void finishJob(job)} />

      {result == null && <p className="mutedText">Select a country, period, and optional budget to run strategic analysis.</p>}

      {result && (
        <div className="workspacePanel">
          <div className="sectionHeader">
            <div>
              <h3>Workflow result</h3>
              <p>
                Status {result.status} · Workflow #{result.workflow_run_id} · MAS #{result.agent_run_id || '-'}
              </p>
            </div>
            <span className={result.status === 'success' ? 'pill success' : 'pill warning'}>{result.status}</span>
          </div>
          {result.warnings.map((warning) => (
            <p key={warning} className="errorText">{warning}</p>
          ))}
          <div className="reportMarkdown">{result.final_answer || 'No final answer was generated.'}</div>

          <h4>Agent progress</h4>
          <div className="stepTimeline">
            {result.steps.map((step) => (
              <div key={step.agent_step_id} className="stepItem">
                <strong>{step.agent_name}</strong>
                <span>{step.step_status}</span>
                <p>{step.summary}</p>
              </div>
            ))}
          </div>

          <h4>Recommendations</h4>
          <div className="compactList">
            {result.recommendations.map((recommendation) => (
              <div key={recommendation.recommendation_id} className="resultCard">
                <strong>{recommendation.title}</strong>
                <p>{recommendation.description}</p>
              </div>
            ))}
          </div>

          {result.budget_allocation.length > 0 && (
            <>
              <h4>Budget allocation</h4>
              <div className="tableWrap">
                <table className="dataTable">
                  <thead>
                    <tr>
                      <th>Channel</th>
                      <th>Share</th>
                      <th>Amount</th>
                      <th>Priority</th>
                      <th>Expected leads</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.budget_allocation.map((item) => (
                      <tr key={item.channel_code}>
                        <td>{item.channel_name || item.channel_code}</td>
                        <td>{Math.round(item.budget_share * 100)}%</td>
                        <td>{numberText(item.budget_amount)}</td>
                        <td>{item.priority}</td>
                        <td>{numberText(item.expected_leads)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          <h4>Evidence</h4>
          <div className="compactList">
            {result.evidence.map((item) => (
              <div key={item.evidence_id} className="resultCard">
                <strong>{item.metric_name || item.source_name}</strong>
                <span>{numberText(item.metric_value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
