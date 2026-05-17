type QualityStatusBadgeProps = {
  status: string | null | undefined;
};

export function QualityStatusBadge({ status }: QualityStatusBadgeProps) {
  const qualityStatus = status ?? 'not_run';

  return <span className={`pill quality-${qualityStatus}`}>{qualityStatus}</span>;
}
