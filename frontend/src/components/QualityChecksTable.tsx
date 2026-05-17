import type { QualityCheck } from '../api/client';
import { QualityStatusBadge } from './QualityStatusBadge';

type QualityChecksTableProps = {
  checks: QualityCheck[];
};

export function QualityChecksTable({ checks }: QualityChecksTableProps) {
  if (checks.length === 0) {
    return <p className="mutedText">No quality checks were recorded.</p>;
  }

  return (
    <div className="tableScroll">
      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Check</th>
            <th>Type</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {checks.map((check) => (
            <tr key={check.check_id}>
              <td>{check.file_name ?? 'run'}</td>
              <td>{check.check_name}</td>
              <td>{check.quality_dimension ?? check.check_type ?? 'unknown'}</td>
              <td>{check.severity ?? 'info'}</td>
              <td>
                <QualityStatusBadge status={check.status} />
              </td>
              <td>{check.message ?? ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
