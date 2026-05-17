import { useCallback, useEffect, useState } from 'react';

import {
  getHistoryAgentRuns,
  getHistoryInsights,
  getHistoryRecommendations,
  getHistoryReports,
  getSavedSummaries,
  updateSavedSummary,
  type HistoryAgentRunItem,
  type HistoryInsightItem,
  type HistoryRecommendationItem,
  type HistoryReportItem,
  type SavedSummaryItem,
} from '../api/client';

type HistoryTab = 'reports' | 'runs' | 'insights' | 'recommendations' | 'summaries';
type DetailItem = HistoryReportItem | HistoryAgentRunItem | HistoryInsightItem | HistoryRecommendationItem | SavedSummaryItem | null;

function detailTitle(detail: DetailItem): string {
  if (!detail) {
    return '';
  }
  if ('title' in detail) {
    return detail.title;
  }
  return detail.user_query;
}

function detailMeta(detail: DetailItem): string[] {
  if (!detail) {
    return [];
  }
  if ('summary_id' in detail) {
    return [
      `Type: ${detail.summary_type}`,
      `Source: ${detail.source_type} #${detail.source_id}`,
      `Object: ${detail.country_name_en ?? detail.domain ?? detail.channel_name ?? '-'}`,
      `Period: ${detail.period_start ?? '-'} - ${detail.period_end ?? '-'}`,
      `RAG: ${detail.rag_ready ? 'ready' : 'not ready'}`,
      `Embedding: ${detail.embedding_status}`,
      `Quality: ${detail.data_quality_status ?? 'unknown'}`,
    ];
  }
  if ('agent_run_id' in detail && 'user_query' in detail) {
    return [
      `Run: #${detail.agent_run_id}`,
      `Country: ${detail.country_name_en ?? '-'}`,
      `Period: ${detail.period_start ?? '-'} - ${detail.period_end ?? '-'}`,
      `Budget: ${detail.budget_amount ? `${detail.budget_amount} ${detail.currency_code}` : '-'}`,
      `Status: ${detail.run_status ?? '-'}`,
      `Confidence: ${detail.confidence_score ?? '-'}`,
    ];
  }
  if ('report_id' in detail) {
    return [
      `Report: #${detail.report_id}`,
      `Type: ${detail.report_type}`,
      `Country: ${detail.country_name_en ?? '-'}`,
      `Period: ${detail.period_start ?? '-'} - ${detail.period_end ?? '-'}`,
      `Quality: ${detail.data_quality_status ?? 'unknown'}`,
      `Status: ${detail.report_status ?? '-'}`,
    ];
  }
  if ('insight_id' in detail) {
    return [
      `Insight: #${detail.insight_id}`,
      `Type: ${detail.insight_type ?? '-'}`,
      `Country: ${detail.country_name_en ?? '-'}`,
      `Severity: ${detail.severity ?? '-'}`,
      `Confidence: ${detail.confidence_score ?? '-'}`,
    ];
  }
  return [
    `Recommendation: #${detail.recommendation_id}`,
    `Type: ${detail.recommendation_type ?? '-'}`,
    `Priority: ${detail.priority ?? '-'}`,
    `Country: ${detail.country_name_en ?? '-'}`,
    `Expected impact: ${detail.expected_impact ?? '-'}`,
    `Confidence: ${detail.confidence_score ?? '-'}`,
  ];
}

function detailBody(detail: DetailItem): string {
  if (!detail) {
    return '';
  }
  if ('summary_text' in detail) {
    return detail.summary_text;
  }
  if ('summary' in detail && detail.summary) {
    return detail.summary;
  }
  if ('description' in detail && detail.description) {
    return detail.description;
  }
  if ('user_query' in detail) {
    return detail.user_query;
  }
  return detail.title;
}

export function KnowledgeHistoryPage() {
  const [activeTab, setActiveTab] = useState<HistoryTab>('reports');
  const [reports, setReports] = useState<HistoryReportItem[]>([]);
  const [runs, setRuns] = useState<HistoryAgentRunItem[]>([]);
  const [insights, setInsights] = useState<HistoryInsightItem[]>([]);
  const [recommendations, setRecommendations] = useState<HistoryRecommendationItem[]>([]);
  const [summaries, setSummaries] = useState<SavedSummaryItem[]>([]);
  const [detail, setDetail] = useState<DetailItem>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const [reportList, runList, insightList, recommendationList, summaryList] = await Promise.all([
        getHistoryReports(),
        getHistoryAgentRuns(),
        getHistoryInsights(),
        getHistoryRecommendations(),
        getSavedSummaries(),
      ]);
      setReports(reportList.items);
      setRuns(runList.items);
      setInsights(insightList.items);
      setRecommendations(recommendationList.items);
      setSummaries(summaryList.items);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown history error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const markReady = async (summary: SavedSummaryItem) => {
    const updatedSummary = await updateSavedSummary(summary.summary_id, { rag_ready: !summary.rag_ready });
    setSummaries((items) => items.map((item) => (item.summary_id === updatedSummary.summary_id ? updatedSummary : item)));
    setDetail(updatedSummary);
  };

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  return (
    <section className="countryOverview" aria-label="Knowledge history">
      <div className="sectionHeader">
        <div>
          <h2>Knowledge History</h2>
          <p>Saved reports, MAS runs, insights, recommendations, and RAG-ready summaries</p>
        </div>
        <button type="button" onClick={() => void loadHistory()} disabled={isLoading}>
          {isLoading ? 'Refreshing' : 'Refresh'}
        </button>
      </div>

      {error !== '' && <p className="errorText">{error}</p>}

      <div className="historyTabs">
        {(['reports', 'runs', 'insights', 'recommendations', 'summaries'] as HistoryTab[]).map((tab) => (
          <button
            key={tab}
            className={activeTab === tab ? 'secondaryButton active' : 'secondaryButton'}
            type="button"
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="historyLayout">
        <div className="overviewPanel">
          {activeTab === 'reports' && (
            <div className="tableScroll">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Country</th>
                    <th>Quality</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((item) => (
                    <tr key={item.report_id} onClick={() => setDetail(item)}>
                      <td>{item.title}</td>
                      <td>{item.report_type}</td>
                      <td>{item.country_name_en ?? '-'}</td>
                      <td><span className={`pill quality-${item.data_quality_status ?? 'unknown'}`}>{item.data_quality_status}</span></td>
                      <td>{item.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'runs' && (
            <div className="tableScroll">
              <table>
                <thead>
                  <tr>
                    <th>Query</th>
                    <th>Country</th>
                    <th>Budget</th>
                    <th>Status</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((item) => (
                    <tr key={item.agent_run_id} onClick={() => setDetail(item)}>
                      <td>{item.user_query}</td>
                      <td>{item.country_name_en ?? '-'}</td>
                      <td>{item.budget_amount ? `${item.budget_amount} ${item.currency_code}` : '-'}</td>
                      <td><span className={`pill ${item.run_status ?? ''}`}>{item.run_status}</span></td>
                      <td>{item.confidence_score ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="tableScroll">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Country</th>
                    <th>Severity</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.map((item) => (
                    <tr key={item.insight_id} onClick={() => setDetail(item)}>
                      <td>{item.title}</td>
                      <td>{item.insight_type}</td>
                      <td>{item.country_name_en ?? '-'}</td>
                      <td><span className={`pill ${item.severity ?? ''}`}>{item.severity}</span></td>
                      <td>{item.confidence_score ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="tableScroll">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Priority</th>
                    <th>Country</th>
                    <th>Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {recommendations.map((item) => (
                    <tr key={item.recommendation_id} onClick={() => setDetail(item)}>
                      <td>{item.title}</td>
                      <td>{item.recommendation_type}</td>
                      <td><span className={`pill ${item.priority ?? ''}`}>{item.priority}</span></td>
                      <td>{item.country_name_en ?? '-'}</td>
                      <td>{item.expected_impact ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'summaries' && (
            <div className="tableScroll">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Object</th>
                    <th>RAG</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {summaries.map((item) => (
                    <tr key={item.summary_id} onClick={() => setDetail(item)}>
                      <td>{item.title}</td>
                      <td>{item.summary_type}</td>
                      <td>{item.country_name_en ?? item.domain ?? item.channel_name ?? '-'}</td>
                      <td><span className={item.rag_ready ? 'pill success' : 'pill skipped'}>{item.rag_ready ? 'ready' : 'not ready'}</span></td>
                      <td>{item.confidence_score ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <aside className="overviewPanel detailPanel">
          <h3>Details</h3>
          {!detail && <p className="mutedText">Select a saved item to inspect it.</p>}
          {detail && (
            <div className="summaryDetail">
              <h4>{detailTitle(detail)}</h4>
              <p>{detailBody(detail)}</p>
              <dl>
                {detailMeta(detail).map((item) => (
                  <div key={item}>
                    <dt>{item.split(':')[0]}</dt>
                    <dd>{item.substring(item.indexOf(':') + 1).trim()}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
          {detail && 'summary_id' in detail && (
            <button type="button" onClick={() => void markReady(detail)}>
              {detail.rag_ready ? 'Remove RAG-ready' : 'Mark RAG-ready'}
            </button>
          )}
        </aside>
      </div>
    </section>
  );
}
