type ReportQualityBannerProps = {
  status: string | null;
};

export function ReportQualityBanner({ status }: ReportQualityBannerProps) {
  if (status !== 'warning') {
    return null;
  }

  return <div className="qualityWarning">Report generated with data quality warnings.</div>;
}
