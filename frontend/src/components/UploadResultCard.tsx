import type { UploadRunResult } from '../api/client';
import { QualityStatusBadge } from './QualityStatusBadge';
import { UploadErrorsPanel } from './UploadErrorsPanel';
import { UploadFilesTable } from './UploadFilesTable';

type UploadResultCardProps = {
  result: UploadRunResult | null;
};

export function UploadResultCard({ result }: UploadResultCardProps) {
  if (!result) {
    return null;
  }

  return (
    <section className="uploadResult" aria-label="Upload result">
      <div className="sectionHeader">
        <div>
          <h2>Upload result</h2>
          <p>Run #{result.run_id}</p>
        </div>
        <div className="qualityActions">
          <span className={`pill ${result.status}`}>{result.status}</span>
          <QualityStatusBadge status={result.quality_status} />
        </div>
      </div>
      <div className="summaryGrid">
        <div>
          <span>Rows</span>
          <strong>{result.row_count}</strong>
        </div>
        <div>
          <span>Files</span>
          <strong>{result.files.length}</strong>
        </div>
      </div>
      <UploadFilesTable files={result.files} />
      <UploadErrorsPanel files={result.files} warnings={result.warnings} />
    </section>
  );
}
