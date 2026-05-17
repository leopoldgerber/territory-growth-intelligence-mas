import type { HealthStatus } from '../api/client';

type SystemStatusCardProps = {
  health: HealthStatus | null;
  isLoading: boolean;
  error: string;
  onRefresh: () => void;
};

function StatusValue({ label, value }: { label: string; value: string }) {
  const statusClass = value === 'ok' ? 'statusValue ok' : 'statusValue warning';

  return (
    <div className="statusRow">
      <span>{label}</span>
      <strong className={statusClass}>{value.toUpperCase()}</strong>
    </div>
  );
}

export function SystemStatusCard({ health, isLoading, error, onRefresh }: SystemStatusCardProps) {
  const backendStatus = health?.backend ?? 'unknown';
  const databaseStatus = health?.database ?? 'unknown';
  const systemStatus = health?.status ?? 'unknown';

  return (
    <section className="statusPanel" aria-label="System status">
      <div className="statusHeader">
        <div>
          <h2>System status</h2>
          <p>{health?.app_name ?? 'Territory Growth Intelligence MAS'}</p>
        </div>
        <button type="button" onClick={onRefresh} disabled={isLoading}>
          {isLoading ? 'Refreshing' : 'Refresh status'}
        </button>
      </div>

      <div className="statusGrid">
        <StatusValue label="Backend" value={backendStatus} />
        <StatusValue label="Database" value={databaseStatus} />
        <StatusValue label="Environment" value={health?.environment ?? 'unknown'} />
        <StatusValue label="Overall" value={systemStatus} />
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
    </section>
  );
}
