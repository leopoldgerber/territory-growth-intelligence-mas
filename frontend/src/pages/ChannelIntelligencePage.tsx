import { useCallback, useEffect, useState } from 'react';

import {
  getChannelSummary,
  getChannelTrend,
  getCompetitorPeriod,
  getCompetitors,
  getCountries,
  getCountryPeriod,
  getJourneySources,
  type ChannelSummary,
  type ChannelTrendItem,
  type CompetitorItem,
  type CountryItem,
  type JourneySourceItem,
} from '../api/client';
import { ChannelMetricsTable } from '../components/ChannelMetricsTable';
import { ChannelRecommendationHints } from '../components/ChannelRecommendationHints';
import { ChannelShareChart } from '../components/ChannelShareChart';
import { ChannelSummaryCards } from '../components/ChannelSummaryCards';
import { ChannelTrendChart } from '../components/ChannelTrendChart';
import { CompetitorSelector } from '../components/CompetitorSelector';
import { CountrySelector } from '../components/CountrySelector';
import { DataQualityWarningBanner } from '../components/DataQualityWarningBanner';
import { JourneySourcesTable } from '../components/JourneySourcesTable';
import { PeriodSelector } from '../components/PeriodSelector';

type ChannelScopeMode = 'country' | 'domain' | 'country_domain' | 'global';

export function ChannelIntelligencePage() {
  const [countries, setCountries] = useState<CountryItem[]>([]);
  const [competitors, setCompetitors] = useState<CompetitorItem[]>([]);
  const [scopeMode, setScopeMode] = useState<ChannelScopeMode>('country');
  const [countryId, setCountryId] = useState<number | null>(null);
  const [domainId, setDomainId] = useState<number | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [summary, setSummary] = useState<ChannelSummary | null>(null);
  const [trend, setTrend] = useState<ChannelTrendItem[]>([]);
  const [sources, setSources] = useState<JourneySourceItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const activeCountryId = scopeMode === 'country' || scopeMode === 'country_domain' ? countryId : null;
  const activeDomainId = scopeMode === 'domain' || scopeMode === 'country_domain' ? domainId : null;

  const loadReferences = useCallback(async () => {
    const countryList = await getCountries();
    const competitorList = await getCompetitors();
    setCountries(countryList.items);
    setCompetitors(competitorList.items);
    if (countryList.items.length > 0) {
      setCountryId(countryList.items[0].country_id);
    }
    if (competitorList.items.length > 0) {
      setDomainId(competitorList.items[0].domain_id);
    }
  }, []);

  const loadPeriod = useCallback(async () => {
    if (activeCountryId != null) {
      const countryPeriod = await getCountryPeriod(activeCountryId);
      setDateFrom(countryPeriod.date_min ?? '');
      setDateTo(countryPeriod.date_max ?? '');
      return;
    }
    if (activeDomainId != null) {
      const competitorPeriod = await getCompetitorPeriod(activeDomainId);
      setDateFrom(competitorPeriod.date_min ?? '');
      setDateTo(competitorPeriod.date_max ?? '');
    }
  }, [activeCountryId, activeDomainId]);

  const loadChannels = useCallback(async () => {
    if (dateFrom === '' || dateTo === '') {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const channelSummary = await getChannelSummary(dateFrom, dateTo, activeCountryId, activeDomainId);
      const channelTrend = await getChannelTrend(dateFrom, dateTo, activeCountryId, activeDomainId);
      const journeySources = await getJourneySources(dateFrom, dateTo, activeCountryId, activeDomainId);
      setSummary(channelSummary);
      setTrend(channelTrend.items);
      setSources(journeySources.items);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown channel analysis error';
      setError(message);
      setSummary(null);
      setTrend([]);
      setSources([]);
    } finally {
      setIsLoading(false);
    }
  }, [activeCountryId, activeDomainId, dateFrom, dateTo]);

  useEffect(() => {
    void loadReferences();
  }, [loadReferences]);

  useEffect(() => {
    void loadPeriod();
  }, [loadPeriod]);

  useEffect(() => {
    void loadChannels();
  }, [loadChannels]);

  return (
    <section className="countryOverview" aria-label="Channel intelligence">
      <div className="sectionHeader">
        <div>
          <h2>Channel Intelligence</h2>
          <p>Acquisition channels, stability, dependency, and journey sources</p>
        </div>
      </div>

      <div className="channelFilters">
        <label>
          <span>Scope</span>
          <select value={scopeMode} onChange={(event) => setScopeMode(event.target.value as ChannelScopeMode)}>
            <option value="country">Country</option>
            <option value="domain">Competitor</option>
            <option value="country_domain">Country + Competitor</option>
            <option value="global">Global</option>
          </select>
        </label>
        {(scopeMode === 'country' || scopeMode === 'country_domain') && (
          <CountrySelector countries={countries} countryId={countryId} onCountryChange={setCountryId} />
        )}
        {(scopeMode === 'domain' || scopeMode === 'country_domain') && (
          <CompetitorSelector competitors={competitors} domainId={domainId} onCompetitorChange={setDomainId} />
        )}
        <PeriodSelector
          dateFrom={dateFrom}
          dateTo={dateTo}
          dateMin={null}
          dateMax={null}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
        />
        <button type="button" onClick={loadChannels} disabled={isLoading}>
          {isLoading ? 'Loading' : 'Refresh channels'}
        </button>
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
      {!summary && !error && <p className="mutedText">Upload channel data to see channel intelligence.</p>}

      {summary && (
        <>
          {summary.warnings.map((warning) => (
            <DataQualityWarningBanner key={warning} warning={warning} />
          ))}
          <ChannelSummaryCards summary={summary.summary} />
          <div className="overviewCharts">
            <ChannelShareChart channels={summary.channels} />
            <ChannelTrendChart trend={trend} />
          </div>
          <ChannelMetricsTable channels={summary.channels} />
          <JourneySourcesTable sources={sources} />
          <ChannelRecommendationHints hints={summary.recommendation_hints} />
        </>
      )}
    </section>
  );
}
