import type { UploadRunSummary } from '../api/client';
import { QualityStatusBadge } from './QualityStatusBadge';

type UploadHistoryTableProps = {
  runs: UploadRunSummary[];
  isLoading: boolean;
};

export function UploadHistoryTable({ runs, isLoading }: UploadHistoryTableProps) {
  return (
    <section className="historyPanel" aria-label="Upload history">
      <div className="sectionHeader">
        <div>
          <h2>Upload history</h2>
          <p>{isLoading ? 'Loading' : `${runs.length} recent runs`}</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Run</th>
              <th>Source</th>
              <th>Status</th>
              <th>Quality</th>
              <th>Rows</th>
              <th>Started</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.run_id}>
                <td>#{run.run_id}</td>
                <td>{run.source_name ?? 'unknown'}</td>
                <td>
                  <span className={`pill ${run.status ?? 'unknown'}`}>{run.status ?? 'unknown'}</span>
                </td>
                <td>
                  <QualityStatusBadge status={run.quality_status} />
                </td>
                <td>{run.row_count}</td>
                <td>{run.started_at ?? 'unknown'}</td>
              </tr>
            ))}
            {runs.length === 0 && (
              <tr>
                <td colSpan={6}>No uploads yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
