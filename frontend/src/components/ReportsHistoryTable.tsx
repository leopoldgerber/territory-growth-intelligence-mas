import type { ReportListItem } from '../api/client';

type ReportsHistoryTableProps = {
  reports: ReportListItem[];
  onReportSelect: (reportId: number) => void;
};

export function ReportsHistoryTable({ reports, onReportSelect }: ReportsHistoryTableProps) {
  return (
    <section className="reportPanel" aria-label="Reports history">
      <div className="sectionHeader">
        <div>
          <h2>Reports history</h2>
          <p>{reports.length} saved reports</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Report</th>
              <th>Country</th>
              <th>Period</th>
              <th>Quality</th>
              <th>Created</th>
              <th>Open</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.report_id}>
                <td>{report.title}</td>
                <td>{report.country_name_en ?? 'n/a'}</td>
                <td>
                  {report.period_start} - {report.period_end}
                </td>
                <td>
                  <span className={`pill quality-${report.data_quality_status ?? 'not_run'}`}>
                    {report.data_quality_status ?? 'unknown'}
                  </span>
                </td>
                <td>{report.created_at ?? 'n/a'}</td>
                <td>
                  <button type="button" onClick={() => onReportSelect(report.report_id)}>
                    Open
                  </button>
                </td>
              </tr>
            ))}
            {reports.length === 0 && (
              <tr>
                <td colSpan={6}>No reports generated yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
