import { useCallback, useEffect, useState } from 'react';

import { getCountries, getCountryPeriod, getOpportunityCountries, type OpportunityCountryItem } from '../api/client';
import { OpportunityRankingTable } from '../components/OpportunityRankingTable';
import { PeriodSelector } from '../components/PeriodSelector';

export function OpportunitiesPage() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [priority, setPriority] = useState('');
  const [items, setItems] = useState<OpportunityCountryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadPeriod = useCallback(async () => {
    const countries = await getCountries();
    if (countries.items.length === 0) {
      return;
    }
    const period = await getCountryPeriod(countries.items[0].country_id);
    setDateFrom(period.date_min ?? '');
    setDateTo(period.date_max ?? '');
  }, []);

  const loadRanking = useCallback(async () => {
    if (dateFrom === '' || dateTo === '') {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const ranking = await getOpportunityCountries(dateFrom, dateTo, priority);
      setItems(ranking.items);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown opportunity ranking error';
      setError(message);
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  }, [dateFrom, dateTo, priority]);

  useEffect(() => {
    void loadPeriod();
  }, [loadPeriod]);

  useEffect(() => {
    void loadRanking();
  }, [loadRanking]);

  return (
    <section className="countryOverview" aria-label="Opportunities">
      <div className="sectionHeader">
        <div>
          <h2>Opportunities</h2>
          <p>Country ranking by opportunity score</p>
        </div>
      </div>
      <div className="overviewFilters">
        <label>
          <span>Priority</span>
          <select value={priority} onChange={(event) => setPriority(event.target.value)}>
            <option value="">All priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="avoid">Avoid</option>
          </select>
        </label>
        <PeriodSelector
          dateFrom={dateFrom}
          dateTo={dateTo}
          dateMin={null}
          dateMax={null}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
        />
        <button type="button" onClick={loadRanking} disabled={isLoading}>
          {isLoading ? 'Loading' : 'Refresh ranking'}
        </button>
      </div>
      {error !== '' && <p className="errorText">{error}</p>}
      <OpportunityRankingTable items={items} />
    </section>
  );
}
