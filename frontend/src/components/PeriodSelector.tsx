type PeriodSelectorProps = {
  dateFrom: string;
  dateTo: string;
  dateMin: string | null;
  dateMax: string | null;
  onDateFromChange: (dateFrom: string) => void;
  onDateToChange: (dateTo: string) => void;
};

export function PeriodSelector({
  dateFrom,
  dateTo,
  dateMin,
  dateMax,
  onDateFromChange,
  onDateToChange,
}: PeriodSelectorProps) {
  return (
    <>
      <label>
        <span>Date from</span>
        <input
          max={dateMax ?? undefined}
          min={dateMin ?? undefined}
          type="date"
          value={dateFrom}
          onChange={(event) => onDateFromChange(event.target.value)}
        />
      </label>
      <label>
        <span>Date to</span>
        <input
          max={dateMax ?? undefined}
          min={dateMin ?? undefined}
          type="date"
          value={dateTo}
          onChange={(event) => onDateToChange(event.target.value)}
        />
      </label>
    </>
  );
}
