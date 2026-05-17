import type { CompetitorItem } from '../api/client';

type CompetitorSelectorProps = {
  competitors: CompetitorItem[];
  domainId: number | null;
  onCompetitorChange: (domainId: number) => void;
};

export function CompetitorSelector({ competitors, domainId, onCompetitorChange }: CompetitorSelectorProps) {
  return (
    <label>
      <span>Competitor</span>
      <select value={domainId ?? ''} onChange={(event) => onCompetitorChange(Number(event.target.value))}>
        <option value="">Select competitor</option>
        {competitors.map((competitor) => (
          <option key={competitor.domain_id} value={competitor.domain_id}>
            {competitor.company_name ?? competitor.domain}
          </option>
        ))}
      </select>
    </label>
  );
}
