import { useCallback, useEffect, useState } from 'react';

import {
  createBudgetStrategy,
  getBudgetStrategies,
  getBudgetStrategy,
  getCountries,
  getCountryPeriod,
  type BudgetStrategyListItem,
  type BudgetStrategyResponse,
  type CountryItem,
} from '../api/client';
import { BudgetStrategyHistoryTable } from '../components/BudgetStrategyHistoryTable';
import { BudgetStrategyResult } from '../components/BudgetStrategyResult';
import { CountrySelector } from '../components/CountrySelector';
import { PeriodSelector } from '../components/PeriodSelector';

export function BudgetStrategyPage() {
  const [countries, setCountries] = useState<CountryItem[]>([]);
  const [countryId, setCountryId] = useState<number | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [budgetAmount, setBudgetAmount] = useState(10000);
  const [currencyCode, setCurrencyCode] = useState('EUR');
  const [campaignGoal, setCampaignGoal] = useState('market_test');
  const [riskAppetite, setRiskAppetite] = useState('medium');
  const [strategy, setStrategy] = useState<BudgetStrategyResponse | null>(null);
  const [history, setHistory] = useState<BudgetStrategyListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const loadCountries = useCallback(async () => {
    const countryList = await getCountries();
    setCountries(countryList.items);
    if (countryList.items.length > 0) {
      setCountryId(countryList.items[0].country_id);
    }
  }, []);

  const loadPeriod = useCallback(async (selectedCountryId: number) => {
    const period = await getCountryPeriod(selectedCountryId);
    setDateFrom(period.date_min ?? '');
    setDateTo(period.date_max ?? '');
  }, []);

  const loadHistory = useCallback(async () => {
    const strategies = await getBudgetStrategies();
    setHistory(strategies.items);
  }, []);

  const generateStrategy = async () => {
    if (!countryId || dateFrom === '' || dateTo === '') {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const createdStrategy = await createBudgetStrategy({
        country_id: countryId,
        date_from: dateFrom,
        date_to: dateTo,
        budget_amount: budgetAmount,
        currency_code: currencyCode,
        campaign_goal: campaignGoal,
        risk_appetite: riskAppetite,
        assumptions: null,
        calculation_version: 'v1',
      });
      setStrategy(createdStrategy);
      await loadHistory();
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown budget strategy error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const openStrategy = async (strategyId: number) => {
    const savedStrategy = await getBudgetStrategy(strategyId);
    setStrategy(savedStrategy);
  };

  useEffect(() => {
    void loadCountries();
    void loadHistory();
  }, [loadCountries, loadHistory]);

  useEffect(() => {
    if (countryId) {
      void loadPeriod(countryId);
    }
  }, [countryId, loadPeriod]);

  return (
    <section className="countryOverview" aria-label="Budget strategy">
      <div className="sectionHeader">
        <div>
          <h2>Budget Strategy</h2>
          <p>Budget allocation by channel and expected effect</p>
        </div>
      </div>

      <div className="strategyForm">
        <CountrySelector countries={countries} countryId={countryId} onCountryChange={setCountryId} />
        <PeriodSelector
          dateFrom={dateFrom}
          dateTo={dateTo}
          dateMin={null}
          dateMax={null}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
        />
        <label>
          <span>Budget</span>
          <input min="1" type="number" value={budgetAmount} onChange={(event) => setBudgetAmount(Number(event.target.value))} />
        </label>
        <label>
          <span>Currency</span>
          <input maxLength={3} value={currencyCode} onChange={(event) => setCurrencyCode(event.target.value.toUpperCase())} />
        </label>
        <label>
          <span>Goal</span>
          <select value={campaignGoal} onChange={(event) => setCampaignGoal(event.target.value)}>
            <option value="market_test">Market test</option>
            <option value="growth">Growth</option>
            <option value="aggressive_entry">Aggressive entry</option>
            <option value="brand_awareness">Brand awareness</option>
            <option value="performance">Performance</option>
          </select>
        </label>
        <label>
          <span>Risk appetite</span>
          <select value={riskAppetite} onChange={(event) => setRiskAppetite(event.target.value)}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        <button type="button" onClick={generateStrategy} disabled={isLoading}>
          {isLoading ? 'Generating' : 'Generate strategy'}
        </button>
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
      <BudgetStrategyResult strategy={strategy} />
      <BudgetStrategyHistoryTable items={history} onStrategySelect={openStrategy} />
    </section>
  );
}
