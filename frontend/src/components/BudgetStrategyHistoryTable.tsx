import type { BudgetStrategyListItem } from '../api/client';

function formatMoney(value: number, currency: string) {
  return new Intl.NumberFormat('en-US', { currency, maximumFractionDigits: 0, style: 'currency' }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value == null ? 'n/a' : `${(value * 100).toFixed(1)}%`;
}

type BudgetStrategyHistoryTableProps = {
  items: BudgetStrategyListItem[];
  onStrategySelect: (strategyId: number) => void;
};

export function BudgetStrategyHistoryTable({ items, onStrategySelect }: BudgetStrategyHistoryTableProps) {
  return (
    <section className="overviewPanel" aria-label="Budget strategy history">
      <div className="sectionHeader">
        <div>
          <h2>Strategy history</h2>
          <p>{items.length} saved strategies</p>
        </div>
      </div>
      <div className="tableScroll">
        <table>
          <thead>
            <tr>
              <th>Country</th>
              <th>Period</th>
              <th>Budget</th>
              <th>Goal</th>
              <th>Type</th>
              <th>Confidence</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.strategy_id}>
                <td>{item.country_name_en}</td>
                <td>
                  {item.period_start} · {item.period_end}
                </td>
                <td>{formatMoney(item.budget_amount, item.currency_code)}</td>
                <td>{item.campaign_goal ?? 'n/a'}</td>
                <td>{item.recommended_strategy_type ?? 'n/a'}</td>
                <td>{formatPercent(item.confidence_score)}</td>
                <td>
                  <button type="button" onClick={() => onStrategySelect(item.strategy_id)}>
                    Open
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={7}>No saved budget strategies yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
