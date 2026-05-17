import { useCallback, useEffect, useState } from 'react';

import {
  detectAlerts,
  getAlertDetail,
  getAlerts,
  getAlertSummary,
  updateAlertStatus,
  type AlertDetail,
  type AlertFilters,
  type AlertItem,
  type AlertSummary,
  type JobItem,
} from '../api/client';
import { JobProgressPanel } from '../components/JobProgressPanel';

const initialFilters: AlertFilters = {
  countryId: '',
  domainId: '',
  channelId: '',
  eventType: '',
  eventCategory: '',
  severity: '',
  status: 'new',
  dateFrom: '',
  dateTo: '',
};

function formatPercent(value: number | null): string {
  if (value == null) {
    return '-';
  }
  return `${Math.round(value * 100)}%`;
}

function formatNumber(value: number | null): string {
  if (value == null) {
    return '-';
  }
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
}

function statusClass(value: string | null): string {
  return `statusBadge ${(value || 'unknown').toLowerCase()}`;
}

function severityClass(value: string | null): string {
  return `severityBadge ${(value || 'unknown').toLowerCase()}`;
}

export function AlertsPage() {
  const [summary, setSummary] = useState<AlertSummary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<AlertDetail | null>(null);
  const [filters, setFilters] = useState<AlertFilters>(initialFilters);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [message, setMessage] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState('');

  const loadAlerts = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const [summaryData, alertData] = await Promise.all([getAlertSummary(), getAlerts(filters)]);
      setSummary(summaryData);
      setAlerts(alertData.items);
    } catch (requestError) {
      const errorMessage = requestError instanceof Error ? requestError.message : 'Unknown alerts error';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadAlerts();
  }, [loadAlerts]);

  const openAlert = async (alert: AlertItem) => {
    setError('');
    try {
      const detail = await getAlertDetail(alert.anomaly_id);
      setSelectedAlert(detail);
    } catch (requestError) {
      const errorMessage = requestError instanceof Error ? requestError.message : 'Unknown alert detail error';
      setError(errorMessage);
    }
  };

  const updateStatus = async (status: string) => {
    if (selectedAlert == null) {
      return;
    }
    setError('');
    try {
      const detail = await updateAlertStatus(selectedAlert.anomaly_id, status);
      setSelectedAlert(detail);
      await loadAlerts();
    } catch (requestError) {
      const errorMessage = requestError instanceof Error ? requestError.message : 'Unknown status update error';
      setError(errorMessage);
    }
  };

  const runDetection = async () => {
    if (filters.dateFrom === '' || filters.dateTo === '') {
      setError('Select date range before running detection.');
      return;
    }
    setIsDetecting(true);
    setError('');
    setMessage('');
    try {
      const queuedJob = await detectAlerts({
        date_from: filters.dateFrom,
        date_to: filters.dateTo,
        country_id: filters.countryId === '' ? null : Number(filters.countryId),
        domain_id: filters.domainId === '' ? null : Number(filters.domainId),
        calculation_version: 'v1',
      });
      setJobId(queuedJob.job_id);
      setMessage(queuedJob.message);
    } catch (requestError) {
      const errorMessage = requestError instanceof Error ? requestError.message : 'Unknown detection error';
      setError(errorMessage);
    } finally {
      setIsDetecting(false);
    }
  };

  const finishJob = async (job: JobItem) => {
    if (job.result_payload != null) {
      const detectedEvents = job.result_payload.detected_events ?? 0;
      const createdEvents = job.result_payload.created_events ?? 0;
      const duplicatesSkipped = job.result_payload.duplicates_skipped ?? 0;
      setMessage(`Detected ${detectedEvents} events, created ${createdEvents}, updated ${duplicatesSkipped}.`);
    }
    await loadAlerts();
    setIsDetecting(false);
  };

  const updateFilter = (key: keyof AlertFilters, value: string) => {
    setFilters((currentFilters) => ({ ...currentFilters, [key]: value }));
  };

  return (
    <section className="alertsPage" aria-label="Alerts">
      <div className="sectionHeader">
        <div>
          <h2>Alerts</h2>
          <p>Rule-based market, competitor, channel, and quality signals detected from uploaded facts.</p>
        </div>
        <button className="primaryButton" type="button" onClick={runDetection} disabled={isDetecting}>
          {isDetecting ? 'Detecting...' : 'Run detection'}
        </button>
      </div>

      {summary && (
        <div className="summaryGrid">
          <div className="summaryCard">
            <span>New alerts</span>
            <strong>{summary.total_new}</strong>
          </div>
          <div className="summaryCard">
            <span>Critical</span>
            <strong>{summary.critical}</strong>
          </div>
          <div className="summaryCard">
            <span>High severity</span>
            <strong>{summary.high}</strong>
          </div>
          <div className="summaryCard">
            <span>Medium</span>
            <strong>{summary.medium}</strong>
          </div>
        </div>
      )}

      <div className="filterGrid">
        <label>
          Country ID
          <input value={filters.countryId} onChange={(event) => updateFilter('countryId', event.target.value)} />
        </label>
        <label>
          Competitor ID
          <input value={filters.domainId} onChange={(event) => updateFilter('domainId', event.target.value)} />
        </label>
        <label>
          Channel ID
          <input value={filters.channelId} onChange={(event) => updateFilter('channelId', event.target.value)} />
        </label>
        <label>
          Type
          <input value={filters.eventType} onChange={(event) => updateFilter('eventType', event.target.value)} />
        </label>
        <label>
          Category
          <select value={filters.eventCategory} onChange={(event) => updateFilter('eventCategory', event.target.value)}>
            <option value="">All</option>
            <option value="traffic">Traffic</option>
            <option value="market">Market</option>
            <option value="channel">Channel</option>
            <option value="quality">Quality</option>
          </select>
        </label>
        <label>
          Severity
          <select value={filters.severity} onChange={(event) => updateFilter('severity', event.target.value)}>
            <option value="">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>
        <label>
          Status
          <select value={filters.status} onChange={(event) => updateFilter('status', event.target.value)}>
            <option value="">All</option>
            <option value="new">New</option>
            <option value="reviewed">Reviewed</option>
            <option value="dismissed">Dismissed</option>
          </select>
        </label>
        <label>
          From
          <input type="date" value={filters.dateFrom} onChange={(event) => updateFilter('dateFrom', event.target.value)} />
        </label>
        <label>
          To
          <input type="date" value={filters.dateTo} onChange={(event) => updateFilter('dateTo', event.target.value)} />
        </label>
      </div>

      {message && <p className="successText">{message}</p>}
      {error && <p className="errorText">{error}</p>}
      {isLoading && <p className="mutedText">Loading alerts...</p>}
      <JobProgressPanel jobId={jobId} title="Alert detection progress" onComplete={(job) => void finishJob(job)} />

      <div className="tableWrap">
        <table className="dataTable">
          <thead>
            <tr>
              <th>Date</th>
              <th>Severity</th>
              <th>Type</th>
              <th>Country</th>
              <th>Competitor</th>
              <th>Channel</th>
              <th>Title</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.anomaly_id}>
                <td>{alert.event_date}</td>
                <td>
                  <span className={severityClass(alert.severity)}>{alert.severity || 'unknown'}</span>
                </td>
                <td>{alert.event_type}</td>
                <td>{alert.country?.country_name_en || '-'}</td>
                <td>{alert.competitor?.domain || '-'}</td>
                <td>{alert.channel?.channel_name || '-'}</td>
                <td>{alert.title}</td>
                <td>
                  <span className={statusClass(alert.status)}>{alert.status}</span>
                </td>
                <td>
                  <button className="secondaryButton compact" type="button" onClick={() => void openAlert(alert)}>
                    Open
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedAlert && (
        <aside className="detailDrawer" aria-label="Alert details">
          <div className="sectionHeader">
            <div>
              <h3>{selectedAlert.title}</h3>
              <p>{selectedAlert.description}</p>
            </div>
            <button className="secondaryButton compact" type="button" onClick={() => setSelectedAlert(null)}>
              Close
            </button>
          </div>
          <dl className="detailList">
            <dt>Type</dt>
            <dd>{selectedAlert.event_type}</dd>
            <dt>Metric</dt>
            <dd>{selectedAlert.metric_name || '-'}</dd>
            <dt>Previous</dt>
            <dd>{formatNumber(selectedAlert.previous_value)}</dd>
            <dt>Current</dt>
            <dd>{formatNumber(selectedAlert.current_value)}</dd>
            <dt>Relative change</dt>
            <dd>{formatPercent(selectedAlert.relative_change)}</dd>
            <dt>Quality</dt>
            <dd>{selectedAlert.data_quality_status || 'unknown'}</dd>
          </dl>
          <div className="recommendationBox">{selectedAlert.recommendation_hint}</div>
          <pre className="jsonPanel">{JSON.stringify(selectedAlert.evidence, null, 2)}</pre>
          <div className="buttonRow">
            <button className="primaryButton" type="button" onClick={() => void updateStatus('reviewed')}>
              Mark reviewed
            </button>
            <button className="secondaryButton" type="button" onClick={() => void updateStatus('dismissed')}>
              Dismiss
            </button>
          </div>
        </aside>
      )}
    </section>
  );
}
