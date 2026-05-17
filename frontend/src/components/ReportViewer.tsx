import type { ReportResponse } from '../api/client';
import { ReportMarkdownViewer } from './ReportMarkdownViewer';
import { ReportQualityBanner } from './ReportQualityBanner';

type ReportViewerProps = {
  report: ReportResponse | null;
};

export function ReportViewer({ report }: ReportViewerProps) {
  if (!report) {
    return null;
  }

  return (
    <section className="reportPanel" aria-label="Report viewer">
      <div className="sectionHeader">
        <div>
          <h2>{report.title}</h2>
          <p>
            Report #{report.report_id} / {report.created_at ?? 'just now'}
          </p>
        </div>
        <span className={`pill quality-${report.data_quality_status ?? 'not_run'}`}>
          {report.data_quality_status ?? 'unknown'}
        </span>
      </div>
      <ReportQualityBanner status={report.data_quality_status} />
      <ReportMarkdownViewer markdown={report.report_markdown ?? ''} />
    </section>
  );
}
