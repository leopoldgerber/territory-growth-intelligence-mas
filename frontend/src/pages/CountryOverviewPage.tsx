import { useCallback, useEffect, useState } from 'react';

import {
  createCountryReport,
  getCountries,
  getCountryDailyMetrics,
  getCountryMetrics,
  getCountryPeriod,
  getOpportunityScore,
  getReport,
  getReports,
  getCountrySummary,
  type CountryItem,
  type CountryMetricsResponse,
  type CountryPeriod,
  type CountrySummary,
  type DailyMetricItem,
  type OpportunityScore,
  type ReportListItem,
  type ReportResponse,
  type JobItem,
} from '../api/client';
import { CountryMetricsPanel } from '../components/CountryMetricsPanel';
import { GenerateCountryReportButton } from '../components/GenerateCountryReportButton';
import { JobProgressPanel } from '../components/JobProgressPanel';
import { ReportViewer } from '../components/ReportViewer';
import { ReportsHistoryTable } from '../components/ReportsHistoryTable';
import { CountryGeneratedSummary } from '../components/CountryGeneratedSummary';
import { CountrySelector } from '../components/CountrySelector';
import { CountrySummaryCards } from '../components/CountrySummaryCards';
import { DataQualityWarningBanner } from '../components/DataQualityWarningBanner';
import { PeriodSelector } from '../components/PeriodSelector';
import { OpportunityScoreCard } from '../components/OpportunityScoreCard';
import { SplitCard } from '../components/SplitCards';
import { TopCompetitorsTable } from '../components/TopCompetitorsTable';
import { TrafficTrendChart } from '../components/TrafficTrendChart';

export function CountryOverviewPage() {
  const [countries, setCountries] = useState<CountryItem[]>([]);
  const [countryId, setCountryId] = useState<number | null>(null);
  const [period, setPeriod] = useState<CountryPeriod | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [summary, setSummary] = useState<CountrySummary | null>(null);
  const [metrics, setMetrics] = useState<CountryMetricsResponse | null>(null);
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetricItem[]>([]);
  const [opportunity, setOpportunity] = useState<OpportunityScore | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [error, setError] = useState('');

  const loadCountries = useCallback(async () => {
    const countryList = await getCountries();
    setCountries(countryList.items);
    if (countryList.items.length > 0) {
      setCountryId(countryList.items[0].country_id);
    }
  }, []);

  const loadPeriod = useCallback(async (selectedCountryId: number) => {
    const countryPeriod = await getCountryPeriod(selectedCountryId);
    setPeriod(countryPeriod);
    setDateFrom(countryPeriod.date_min ?? '');
    setDateTo(countryPeriod.date_max ?? '');
  }, []);

  const loadSummary = useCallback(async () => {
    if (!countryId || dateFrom === '' || dateTo === '') {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const countrySummary = await getCountrySummary(countryId, dateFrom, dateTo, 10);
      const countryMetrics = await getCountryMetrics(countryId, dateFrom, dateTo);
      const countryDailyMetrics = await getCountryDailyMetrics(countryId, dateFrom, dateTo);
      const opportunityScore = await getOpportunityScore(countryId, dateFrom, dateTo);
      setSummary(countrySummary);
      setMetrics(countryMetrics);
      setDailyMetrics(countryDailyMetrics.items);
      setOpportunity(opportunityScore);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown country summary error';
      setError(message);
      setSummary(null);
      setMetrics(null);
      setDailyMetrics([]);
      setOpportunity(null);
    } finally {
      setIsLoading(false);
    }
  }, [countryId, dateFrom, dateTo]);

  const loadReports = useCallback(async () => {
    const reportList = await getReports();
    setReports(reportList.items);
  }, []);

  const generateReport = async () => {
    if (!countryId || dateFrom === '' || dateTo === '') {
      return;
    }

    setIsGeneratingReport(true);
    setError('');

    try {
      const queuedJob = await createCountryReport({
        country_id: countryId,
        date_from: dateFrom,
        date_to: dateTo,
        limit_competitors: 10,
        include_channels: true,
        include_recommendations: true,
        calculation_version: 'v1',
      });
      setJobId(queuedJob.job_id);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown report generation error';
      setError(message);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const finishJob = async (job: JobItem) => {
    if (job.result_payload != null) {
      setReport(job.result_payload as unknown as ReportResponse);
    }
    await loadReports();
    setIsGeneratingReport(false);
  };

  const openReport = async (reportId: number) => {
    const savedReport = await getReport(reportId);
    setReport(savedReport);
  };

  useEffect(() => {
    void loadCountries();
    void loadReports();
  }, [loadCountries, loadReports]);

  useEffect(() => {
    if (countryId) {
      void loadPeriod(countryId);
    }
  }, [countryId, loadPeriod]);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  return (
    <section className="countryOverview" aria-label="Country overview">
      <div className="sectionHeader">
        <div>
          <h2>Country Overview</h2>
          <p>Market summary by country and period</p>
        </div>
      </div>

      <div className="overviewFilters">
        <CountrySelector countries={countries} countryId={countryId} onCountryChange={setCountryId} />
        <PeriodSelector
          dateFrom={dateFrom}
          dateTo={dateTo}
          dateMin={period?.date_min ?? null}
          dateMax={period?.date_max ?? null}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
        />
        <button type="button" onClick={loadSummary} disabled={isLoading}>
          {isLoading ? 'Loading' : 'Refresh overview'}
        </button>
        <GenerateCountryReportButton
          disabled={!countryId || dateFrom === '' || dateTo === ''}
          isGenerating={isGeneratingReport}
          onGenerate={generateReport}
        />
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
      <JobProgressPanel jobId={jobId} title="Report generation progress" onComplete={(job) => void finishJob(job)} />
      {!summary && !error && <p className="mutedText">Upload country traffic data to see the overview.</p>}

      {summary && (
        <>
          <DataQualityWarningBanner warning={summary.quality_warning} />
          <OpportunityScoreCard opportunity={opportunity} />
          <CountrySummaryCards metrics={summary.summary} />
          <CountryMetricsPanel metrics={metrics} dailyMetrics={dailyMetrics} />
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
          <TopCompetitorsTable competitors={summary.top_competitors} />
          <CountryGeneratedSummary text={summary.generated_summary} />
          <ReportViewer report={report} />
          <ReportsHistoryTable reports={reports} onReportSelect={openReport} />
        </>
      )}
    </section>
  );
}
