import { useCallback, useEffect, useState } from 'react';

import {
  createCampaignSnapshot,
  createForecastComparisons,
  createRecommendationFeedback,
  getCampaignSnapshots,
  getForecastComparisons,
  getLearningSummary,
  getRecommendationFeedback,
  getScoringAdjustments,
  getScoringWeights,
  updateScoringAdjustment,
  type CampaignSnapshotList,
  type ForecastComparisonList,
  type LearningSummary,
  type RecommendationFeedbackList,
  type ScoringWeightAdjustmentList,
  type ScoringWeightVersionList,
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

function formatPercent(value: number | null | undefined): string {
  if (value == null) {
    return 'No data';
  }
  return `${Math.round(value * 100)}%`;
}

export function LearningFeedbackPage() {
  const { activeProject } = useAuth();
  const [summary, setSummary] = useState<LearningSummary | null>(null);
  const [feedback, setFeedback] = useState<RecommendationFeedbackList | null>(null);
  const [snapshots, setSnapshots] = useState<CampaignSnapshotList | null>(null);
  const [comparisons, setComparisons] = useState<ForecastComparisonList | null>(null);
  const [weights, setWeights] = useState<ScoringWeightVersionList | null>(null);
  const [adjustments, setAdjustments] = useState<ScoringWeightAdjustmentList | null>(null);
  const [recommendationId, setRecommendationId] = useState('');
  const [feedbackStatus, setFeedbackStatus] = useState('accepted');
  const [decisionReason, setDecisionReason] = useState('');
  const [decisionTags, setDecisionTags] = useState('strategic_fit');
  const [campaignId, setCampaignId] = useState('');
  const [snapshotStart, setSnapshotStart] = useState(todayOffset(-30));
  const [snapshotEnd, setSnapshotEnd] = useState(todayOffset(-1));
  const [snapshotSpend, setSnapshotSpend] = useState('0');
  const [snapshotVisits, setSnapshotVisits] = useState('0');
  const [snapshotLeads, setSnapshotLeads] = useState('0');
  const [snapshotClients, setSnapshotClients] = useState('0');
  const [snapshotRevenue, setSnapshotRevenue] = useState('0');
  const [scenarioId, setScenarioId] = useState('');
  const [snapshotId, setSnapshotId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadFeedback = useCallback(async () => {
    if (activeProject == null) {
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const projectId = activeProject.project_id;
      const [summaryData, feedbackData, snapshotData, comparisonData, weightData, adjustmentData] = await Promise.all([
        getLearningSummary(projectId),
        getRecommendationFeedback(projectId),
        getCampaignSnapshots(projectId),
        getForecastComparisons(projectId),
        getScoringWeights(projectId),
        getScoringAdjustments(projectId),
      ]);
      setSummary(summaryData);
      setFeedback(feedbackData);
      setSnapshots(snapshotData);
      setComparisons(comparisonData);
      setWeights(weightData);
      setAdjustments(adjustmentData);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Feedback load failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [activeProject]);

  useEffect(() => {
    void loadFeedback();
  }, [loadFeedback]);

  const submitFeedback = async () => {
    if (activeProject == null) {
      return;
    }
    await createRecommendationFeedback(activeProject.project_id, {
      recommendation_id: recommendationId === '' ? null : Number(recommendationId),
      feedback_status: feedbackStatus,
      decision_reason: decisionReason,
      decision_tags: decisionTags.split(',').map((tag) => tag.trim()).filter((tag) => tag !== ''),
    });
    await loadFeedback();
  };

  const submitSnapshot = async () => {
    if (activeProject == null || campaignId === '') {
      return;
    }
    await createCampaignSnapshot(activeProject.project_id, {
      campaign_id: Number(campaignId),
      period_start: snapshotStart,
      period_end: snapshotEnd,
      actual_spend: Number(snapshotSpend),
      visits: Number(snapshotVisits),
      leads: Number(snapshotLeads),
      clients: Number(snapshotClients),
      revenue: Number(snapshotRevenue),
      currency_code: 'EUR',
      data_quality_status: 'passed',
      source_type: 'manual',
    });
    await loadFeedback();
  };

  const submitComparison = async () => {
    if (activeProject == null || snapshotId === '') {
      return;
    }
    await createForecastComparisons(activeProject.project_id, {
      growth_scenario_id: scenarioId === '' ? null : Number(scenarioId),
      campaign_result_snapshot_id: Number(snapshotId),
      recommendation_id: null,
      strategy_id: null,
      metric_names: ['traffic', 'leads', 'clients', 'revenue', 'cac', 'roi'],
    });
    await loadFeedback();
  };

  const changeAdjustment = async (adjustmentId: number, status: string) => {
    if (activeProject == null) {
      return;
    }
    await updateScoringAdjustment(activeProject.project_id, adjustmentId, status);
    await loadFeedback();
  };

  return (
    <section className="countryOverview" aria-label="Learning and feedback">
      <div className="sectionHeader">
        <div>
          <h2>Learning & Feedback</h2>
          <p>Track recommendation decisions, campaign outcomes, forecast accuracy, and reviewed scoring changes.</p>
        </div>
        <button className="secondaryButton" type="button" onClick={loadFeedback} disabled={isLoading || activeProject == null}>
          Refresh
        </button>
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
      {isLoading && <p className="mutedText">Loading feedback loop...</p>}

      <div className="metricGrid">
        <article className="metricCard">
          <span>Acceptance rate</span>
          <strong>{formatPercent(summary?.recommendation_acceptance_rate)}</strong>
          <small>{Object.entries(summary?.recommendation_counts ?? {}).map(([key, value]) => `${key}: ${value}`).join(', ') || 'No decisions yet'}</small>
        </article>
        <article className="metricCard">
          <span>Forecast accuracy</span>
          <strong>{formatPercent(summary?.average_forecast_accuracy)}</strong>
          <small>Average across saved comparisons</small>
        </article>
        <article className="metricCard">
          <span>Snapshots</span>
          <strong>{snapshots?.total ?? 0}</strong>
          <small>Campaign result checkpoints</small>
        </article>
        <article className="metricCard">
          <span>Weight proposals</span>
          <strong>{adjustments?.total ?? 0}</strong>
          <small>Human-reviewed scoring changes</small>
        </article>
      </div>

      <div className="splitLayout">
        <article className="workspacePanel">
          <h3>Recommendation Feedback</h3>
          <div className="formGrid">
            <label>
              Recommendation ID
              <input value={recommendationId} onChange={(event) => setRecommendationId(event.target.value)} placeholder="Optional" />
            </label>
            <label>
              Decision
              <select value={feedbackStatus} onChange={(event) => setFeedbackStatus(event.target.value)}>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
                <option value="deferred">Deferred</option>
                <option value="partially_accepted">Partially accepted</option>
              </select>
            </label>
            <label>
              Tags
              <input value={decisionTags} onChange={(event) => setDecisionTags(event.target.value)} />
            </label>
          </div>
          <label className="queryLabel">
            Reason
            <textarea value={decisionReason} onChange={(event) => setDecisionReason(event.target.value)} />
          </label>
          <button className="primaryButton" type="button" onClick={submitFeedback} disabled={activeProject == null}>
            Save Feedback
          </button>
        </article>

        <article className="workspacePanel">
          <h3>Campaign Result Snapshot</h3>
          <div className="formGrid">
            <label>
              Campaign ID
              <input value={campaignId} onChange={(event) => setCampaignId(event.target.value)} />
            </label>
            <label>
              Period start
              <input type="date" value={snapshotStart} onChange={(event) => setSnapshotStart(event.target.value)} />
            </label>
            <label>
              Period end
              <input type="date" value={snapshotEnd} onChange={(event) => setSnapshotEnd(event.target.value)} />
            </label>
            <label>
              Spend
              <input value={snapshotSpend} onChange={(event) => setSnapshotSpend(event.target.value)} />
            </label>
            <label>
              Visits
              <input value={snapshotVisits} onChange={(event) => setSnapshotVisits(event.target.value)} />
            </label>
            <label>
              Leads
              <input value={snapshotLeads} onChange={(event) => setSnapshotLeads(event.target.value)} />
            </label>
            <label>
              Clients
              <input value={snapshotClients} onChange={(event) => setSnapshotClients(event.target.value)} />
            </label>
            <label>
              Revenue
              <input value={snapshotRevenue} onChange={(event) => setSnapshotRevenue(event.target.value)} />
            </label>
          </div>
          <button className="primaryButton" type="button" onClick={submitSnapshot} disabled={activeProject == null || campaignId === ''}>
            Save Snapshot
          </button>
        </article>
      </div>

      <article className="workspacePanel">
        <h3>Forecast vs Actual</h3>
        <div className="formGrid">
          <label>
            Scenario ID
            <input value={scenarioId} onChange={(event) => setScenarioId(event.target.value)} placeholder="Optional" />
          </label>
          <label>
            Snapshot ID
            <input value={snapshotId} onChange={(event) => setSnapshotId(event.target.value)} />
          </label>
          <button className="primaryButton" type="button" onClick={submitComparison} disabled={activeProject == null || snapshotId === ''}>
            Compare
          </button>
        </div>
        <div className="tableScroll">
          <table className="dataTable">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Forecast</th>
                <th>Actual</th>
                <th>Error</th>
                <th>Accuracy</th>
                <th>Bias</th>
              </tr>
            </thead>
            <tbody>
              {(comparisons?.items ?? []).map((item) => (
                <tr key={item.comparison_id}>
                  <td>{item.metric_name}</td>
                  <td>{formatNumber(item.forecast_value)}</td>
                  <td>{formatNumber(item.actual_value)}</td>
                  <td>{formatPercent(item.relative_error)}</td>
                  <td>{formatPercent(item.accuracy_score)}</td>
                  <td><span className={`pill ${item.bias_direction}`}>{item.bias_direction}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <div className="splitLayout">
        <article className="workspacePanel">
          <h3>Accuracy by Metric</h3>
          <div className="barList">
            {Object.entries(summary?.accuracy_by_metric ?? {}).map(([metric, value]) => (
              <div key={metric} className="barRow">
                <div><span>{metric}</span><strong>{formatPercent(value)}</strong></div>
                <span className="barTrack"><span style={{ width: `${Math.max(2, Math.round(value * 100))}%` }} /></span>
              </div>
            ))}
          </div>
        </article>
        <article className="workspacePanel">
          <h3>Active Scoring Weights</h3>
          <div className="compactList">
            {(weights?.items ?? []).map((item) => (
              <div key={item.weight_version_id} className="resultCard">
                <strong>{item.model_name}</strong>
                <span>{item.version_name} · {item.status}</span>
                <p>{Object.entries(item.weights).map(([key, value]) => `${key}: ${String(value)}`).join(', ')}</p>
              </div>
            ))}
          </div>
        </article>
      </div>

      <article className="workspacePanel">
        <h3>Scoring Weight Proposals</h3>
        <div className="tableScroll">
          <table className="dataTable">
            <thead>
              <tr>
                <th>Model</th>
                <th>Version</th>
                <th>Expected improvement</th>
                <th>Status</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(adjustments?.items ?? []).map((item) => (
                <tr key={item.weight_adjustment_id}>
                  <td>{item.model_name}</td>
                  <td>{item.proposed_version_name}</td>
                  <td>{formatPercent(item.expected_improvement)}</td>
                  <td><span className={`pill ${item.status}`}>{item.status}</span></td>
                  <td>{item.reason}</td>
                  <td>
                    <div className="buttonRow">
                      {['approved', 'rejected', 'applied', 'archived'].map((status) => (
                        <button
                          key={status}
                          className="secondaryButton compact"
                          type="button"
                          onClick={() => void changeAdjustment(item.weight_adjustment_id, status)}
                        >
                          {status}
                        </button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <article className="workspacePanel">
        <h3>Recent Decisions</h3>
        <div className="compactList">
          {(feedback?.items ?? []).map((item) => (
            <div key={item.feedback_id} className="resultCard">
              <strong>{item.feedback_status}</strong>
              <span>Recommendation {item.recommendation_id ?? 'manual'} · Feedback {item.feedback_id}</span>
              <p>{item.decision_reason ?? 'No reason provided.'}</p>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}
