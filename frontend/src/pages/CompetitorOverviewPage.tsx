import { useCallback, useEffect, useState } from 'react';

import {
  getCompetitorPeriod,
  getCompetitorSummary,
  getCompetitors,
  type CompetitorItem,
  type CompetitorPeriod,
  type CompetitorSummary,
} from '../api/client';
import { CompetitorCountriesTable } from '../components/CompetitorCountriesTable';
import { CompetitorGeneratedSummary } from '../components/CompetitorGeneratedSummary';
import { CompetitorSelector } from '../components/CompetitorSelector';
import { CompetitorSignalsPanel } from '../components/CompetitorSignalsPanel';
import { CompetitorSummaryCards } from '../components/CompetitorSummaryCards';
import { DataQualityWarningBanner } from '../components/DataQualityWarningBanner';
import { PeriodSelector } from '../components/PeriodSelector';
import { SplitCard } from '../components/SplitCards';
import { TrafficTrendChart } from '../components/TrafficTrendChart';

export function CompetitorOverviewPage() {
  const [competitors, setCompetitors] = useState<CompetitorItem[]>([]);
  const [domainId, setDomainId] = useState<number | null>(null);
  const [period, setPeriod] = useState<CompetitorPeriod | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [summary, setSummary] = useState<CompetitorSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadCompetitors = useCallback(async () => {
    const competitorList = await getCompetitors();
    setCompetitors(competitorList.items);
    if (competitorList.items.length > 0) {
      setDomainId(competitorList.items[0].domain_id);
    }
  }, []);

  const loadPeriod = useCallback(async (selectedDomainId: number) => {
    const competitorPeriod = await getCompetitorPeriod(selectedDomainId);
    setPeriod(competitorPeriod);
    setDateFrom(competitorPeriod.date_min ?? '');
    setDateTo(competitorPeriod.date_max ?? '');
  }, []);

  const loadSummary = useCallback(async () => {
    if (!domainId || dateFrom === '' || dateTo === '') {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const competitorSummary = await getCompetitorSummary(domainId, dateFrom, dateTo, 10);
      setSummary(competitorSummary);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown competitor summary error';
      setError(message);
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  }, [domainId, dateFrom, dateTo]);

  useEffect(() => {
    void loadCompetitors();
  }, [loadCompetitors]);

  useEffect(() => {
    if (domainId) {
      void loadPeriod(domainId);
    }
  }, [domainId, loadPeriod]);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  return (
    <section className="countryOverview" aria-label="Competitor overview">
      <div className="sectionHeader">
        <div>
          <h2>Competitor Overview</h2>
          <p>Domain performance by country and period</p>
        </div>
      </div>

      <div className="overviewFilters">
        <CompetitorSelector competitors={competitors} domainId={domainId} onCompetitorChange={setDomainId} />
        <PeriodSelector
          dateFrom={dateFrom}
          dateTo={dateTo}
          dateMin={period?.date_min ?? null}
          dateMax={period?.date_max ?? null}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
        />
        <button type="button" onClick={loadSummary} disabled={isLoading}>
          {isLoading ? 'Loading' : 'Refresh competitor'}
        </button>
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
      {!summary && !error && <p className="mutedText">Upload competitor traffic data to see the overview.</p>}

      {summary && (
        <>
          <DataQualityWarningBanner warning={summary.quality_warning} />
          <CompetitorSummaryCards metrics={summary.summary} />
          <div className="overviewCharts">
            <TrafficTrendChart trend={summary.daily_trend} />
            <SplitCard
              title="Desktop vs mobile"
              firstLabel="Desktop"
              firstValue={summary.summary.desktop_share}
              secondLabel="Mobile"
              secondValue={summary.summary.mobile_share}
            />
            <SplitCard
              title="Bounce vs no-bounce"
              firstLabel="No-bounce"
              firstValue={summary.summary.no_bounce_share}
              secondLabel="Bounce"
              secondValue={summary.summary.bounce_share}
            />
          </div>
          <CompetitorCountriesTable countries={summary.top_countries} />
          <CompetitorSignalsPanel signals={summary.signals} />
          <CompetitorGeneratedSummary text={summary.generated_summary} />
        </>
      )}
    </section>
  );
}
