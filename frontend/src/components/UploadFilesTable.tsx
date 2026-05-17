import type { UploadFileResult } from '../api/client';

type UploadFilesTableProps = {
  files: UploadFileResult[];
};

export function UploadFilesTable({ files }: UploadFilesTableProps) {
  if (files.length === 0) {
    return <p className="mutedText">No files were processed.</p>;
  }

  return (
    <div className="tableScroll">
      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Report type</th>
            <th>Status</th>
            <th>Rows</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={`${file.file_name}-${file.file_id ?? 'unknown'}`}>
              <td>{file.file_name}</td>
              <td>{file.report_type}</td>
              <td>
                <span className={`pill ${file.status}`}>{file.status}</span>
              </td>
              <td>{file.row_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
