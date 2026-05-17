import type { UploadFileResult } from '../api/client';

type UploadErrorsPanelProps = {
  files: UploadFileResult[];
  warnings: string[];
};

export function UploadErrorsPanel({ files, warnings }: UploadErrorsPanelProps) {
  const fileMessages = files.flatMap((file) => [
    ...file.errors.map((message) => `${file.file_name}: ${message}`),
    ...file.warnings.map((message) => `${file.file_name}: ${message}`),
  ]);
  const messages = [...warnings, ...fileMessages];

  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="messagePanel">
      {messages.map((message) => (
        <p key={message}>{message}</p>
      ))}
    </div>
  );
}
