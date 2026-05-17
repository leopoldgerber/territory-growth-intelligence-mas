import type { QualityResult, QualitySummary } from '../api/client';
import { QualityChecksTable } from './QualityChecksTable';
import { QualityStatusBadge } from './QualityStatusBadge';

type DataQualitySummaryCardProps = {
  quality: QualityResult | null;
  fallbackStatus?: string;
  fallbackSummary?: QualitySummary | null;
  onRerun?: () => void;
  isRunning?: boolean;
};

export function DataQualitySummaryCard({
  quality,
  fallbackStatus,
  fallbackSummary,
  onRerun,
  isRunning = false,
}: DataQualitySummaryCardProps) {
  const summary = quality?.summary ?? fallbackSummary;
  const status = quality?.quality_status ?? fallbackStatus ?? 'not_run';

  if (!summary) {
    return null;
  }

  return (
    <section className="qualityPanel" aria-label="Data quality summary">
      <div className="sectionHeader">
        <div>
          <h2>Data quality</h2>
          <p>{status === 'failed' ? 'Fix critical checks before analytics.' : 'Quality checks are available.'}</p>
        </div>
        <div className="qualityActions">
          <QualityStatusBadge status={status} />
          {onRerun && (
            <button type="button" onClick={onRerun} disabled={isRunning}>
              {isRunning ? 'Running' : 'Run checks'}
            </button>
          )}
        </div>
      </div>

      <div className="summaryGrid">
        <div>
          <span>Total checks</span>
          <strong>{summary.total_checks}</strong>
        </div>
        <div>
          <span>Passed</span>
          <strong>{summary.passed}</strong>
        </div>
        <div>
          <span>Warnings</span>
          <strong>{summary.warnings}</strong>
        </div>
        <div>
          <span>Failed</span>
          <strong>{summary.failed}</strong>
        </div>
      </div>

      <QualityChecksTable checks={quality?.checks ?? []} />
    </section>
  );
}
