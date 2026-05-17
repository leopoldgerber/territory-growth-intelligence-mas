type ReportMarkdownViewerProps = {
  markdown: string;
};

export function ReportMarkdownViewer({ markdown }: ReportMarkdownViewerProps) {
  return <pre className="reportMarkdown">{markdown}</pre>;
}
