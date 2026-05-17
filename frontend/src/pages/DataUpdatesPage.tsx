import { useCallback, useEffect, useState } from 'react';

import {
  createUpdateSchedule,
  getLatestUpdateStatus,
  getUpdateRuns,
  getUpdateRunSteps,
  getUpdateSchedules,
  runUpdateNow,
  updateUpdateSchedule,
  type JobItem,
  type UpdateLatestStatus,
  type UpdateRunItem,
  type UpdateRunStepItem,
  type UpdateScheduleItem,
} from '../api/client';
import { JobProgressPanel } from '../components/JobProgressPanel';
import { useAuth } from '../components/AuthProvider';

export function DataUpdatesPage() {
  const { activeProject } = useAuth();
  const [freshness, setFreshness] = useState<UpdateLatestStatus | null>(null);
  const [schedules, setSchedules] = useState<UpdateScheduleItem[]>([]);
  const [runs, setRuns] = useState<UpdateRunItem[]>([]);
  const [steps, setSteps] = useState<UpdateRunStepItem[]>([]);
  const [selectedRun, setSelectedRun] = useState<UpdateRunItem | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [scheduleName, setScheduleName] = useState('Weekly import');
  const [frequency, setFrequency] = useState('weekly');
  const [importFolder, setImportFolder] = useState('/app/uploads/scheduled');
  const [lookbackDays, setLookbackDays] = useState(14);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const projectId = activeProject?.project_id ?? null;

  const loadUpdates = useCallback(async () => {
    setError('');
    try {
      const [freshnessData, scheduleData, runData] = await Promise.all([
        getLatestUpdateStatus(projectId),
        getUpdateSchedules(projectId),
        getUpdateRuns(projectId),
      ]);
      setFreshness(freshnessData);
      setSchedules(scheduleData.items);
      setRuns(runData.items);
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Update data request failed';
      setError(detail);
    }
  }, [projectId]);

  useEffect(() => {
    void loadUpdates();
  }, [loadUpdates]);

  const submitSchedule = async () => {
    setError('');
    setMessage('');
    try {
      await createUpdateSchedule({
        project_id: projectId,
        schedule_name: scheduleName,
        update_type: 'file_import',
        frequency,
        cron_expression: null,
        timezone: 'UTC',
        lookback_days: lookbackDays,
        default_granularity: 'daily',
        config: { import_folder: importFolder },
      });
      setMessage('Schedule created.');
      await loadUpdates();
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Schedule create failed';
      setError(detail);
    }
  };

  const toggleSchedule = async (schedule: UpdateScheduleItem) => {
    setError('');
    await updateUpdateSchedule(schedule.schedule_id, { is_active: !schedule.is_active });
    await loadUpdates();
  };

  const runSchedule = async (schedule: UpdateScheduleItem) => {
    setError('');
    setMessage('');
    try {
      const queued = await runUpdateNow(schedule.schedule_id);
      setJobId(queued.job_id);
      setMessage(`Update run #${queued.update_run_id} queued.`);
      await loadUpdates();
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Run now failed';
      setError(detail);
    }
  };

  const openRun = async (run: UpdateRunItem) => {
    setSelectedRun(run);
    const stepData = await getUpdateRunSteps(run.update_run_id);
    setSteps(stepData.items);
    setJobId(run.job_id);
  };

  const finishJob = async (job: JobItem) => {
    setMessage(`Job ${job.status}.`);
    await loadUpdates();
  };

  return (
    <section className="dataUpdatesPage" aria-label="Data updates">
      <div className="sectionHeader">
        <div>
          <h2>Data Updates</h2>
          <p>Manage recurring imports, update runs, and data freshness.</p>
        </div>
        <span className={`pill ${freshness?.data_freshness_status || 'missing'}`}>
          {freshness?.data_freshness_status || 'missing'}
        </span>
      </div>

      <div className="summaryGrid">
        <div>
          <span>Last status</span>
          <strong>{freshness?.last_update_status || 'missing'}</strong>
        </div>
        <div>
          <span>Quality</span>
          <strong>{freshness?.quality_status || 'unknown'}</strong>
        </div>
        <div>
          <span>Latest period</span>
          <strong>{freshness?.latest_data_period.date_from || '-'} to {freshness?.latest_data_period.date_to || '-'}</strong>
        </div>
        <div>
          <span>Alerts</span>
          <strong>{freshness?.alerts_detected_count ?? 0}</strong>
        </div>
      </div>

      <div className="workspacePanel">
        <h3>Create schedule</h3>
        <div className="settingsForm">
          <label>
            Name
            <input value={scheduleName} onChange={(event) => setScheduleName(event.target.value)} />
          </label>
          <label>
            Frequency
            <select value={frequency} onChange={(event) => setFrequency(event.target.value)}>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select>
          </label>
          <label>
            Import folder
            <input value={importFolder} onChange={(event) => setImportFolder(event.target.value)} />
          </label>
          <label>
            Lookback
            <input type="number" value={lookbackDays} onChange={(event) => setLookbackDays(Number(event.target.value))} />
          </label>
          <button type="button" onClick={submitSchedule}>
            Create
          </button>
        </div>
      </div>

      <JobProgressPanel jobId={jobId} title="Update progress" onComplete={(job) => void finishJob(job)} />

      <div className="workspacePanel">
        <h3>Schedules</h3>
        <div className="tableWrap">
          <table className="dataTable">
            <thead>
              <tr>
                <th>Name</th>
                <th>Frequency</th>
                <th>Active</th>
                <th>Next run</th>
                <th>Last status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {schedules.map((schedule) => (
                <tr key={schedule.schedule_id}>
                  <td>{schedule.schedule_name}</td>
                  <td>{schedule.frequency}</td>
                  <td>{schedule.is_active ? 'yes' : 'no'}</td>
                  <td>{schedule.next_run_at || '-'}</td>
                  <td>{schedule.last_run_status || '-'}</td>
                  <td>
                    <div className="buttonRow">
                      <button className="secondaryButton compact" type="button" onClick={() => void runSchedule(schedule)}>
                        Run now
                      </button>
                      <button className="secondaryButton compact" type="button" onClick={() => void toggleSchedule(schedule)}>
                        {schedule.is_active ? 'Pause' : 'Enable'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="workspacePanel">
        <h3>Update history</h3>
        <div className="tableWrap">
          <table className="dataTable">
            <thead>
              <tr>
                <th>ID</th>
                <th>Status</th>
                <th>Period</th>
                <th>Rows</th>
                <th>Quality</th>
                <th>Metrics</th>
                <th>Scores</th>
                <th>Alerts</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.update_run_id} onClick={() => void openRun(run)}>
                  <td>#{run.update_run_id}</td>
                  <td><span className={`pill ${run.status}`}>{run.status}</span></td>
                  <td>{run.period_start || '-'} to {run.period_end || '-'}</td>
                  <td>{run.rows_loaded_count}</td>
                  <td>{run.quality_status}</td>
                  <td>{run.metrics_recalculated ? 'yes' : 'no'}</td>
                  <td>{run.scores_recalculated ? 'yes' : 'no'}</td>
                  <td>{run.alerts_detected_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedRun && (
        <aside className="detailDrawer" aria-label="Update run details">
          <div className="sectionHeader">
            <div>
              <h3>Update run #{selectedRun.update_run_id}</h3>
              <p>{selectedRun.status} · {selectedRun.run_type}</p>
            </div>
            <button className="secondaryButton compact" type="button" onClick={() => setSelectedRun(null)}>
              Close
            </button>
          </div>
          <ol className="jobTimeline">
            {steps.map((step) => (
              <li key={step.update_run_step_id}>
                <strong>{step.step_name}</strong>
                <span>{step.step_status} · {step.message}</span>
              </li>
            ))}
          </ol>
        </aside>
      )}

      {message && <p className="successText">{message}</p>}
      {error && <p className="errorText">{error}</p>}
    </section>
  );
}
