type DataQualityWarningBannerProps = {
  warning: string | null;
};

export function DataQualityWarningBanner({ warning }: DataQualityWarningBannerProps) {
  if (!warning) {
    return null;
  }

  return <div className="qualityWarning">{warning}</div>;
}
