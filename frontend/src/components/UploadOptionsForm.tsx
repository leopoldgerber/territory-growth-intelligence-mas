import type { UploadOptions } from '../api/client';

type UploadOptionsFormProps = {
  options: UploadOptions;
  onOptionsChange: (options: UploadOptions) => void;
};

export function UploadOptionsForm({ options, onOptionsChange }: UploadOptionsFormProps) {
  const updateOption = (name: keyof UploadOptions, value: string | boolean) => {
    onOptionsChange({ ...options, [name]: value });
  };

  return (
    <div className="uploadOptions">
      <label>
        <span>Source</span>
        <select value={options.sourceName} onChange={(event) => updateOption('sourceName', event.target.value)}>
          <option value="manual_upload">manual_upload</option>
          <option value="semrush_parser">semrush_parser</option>
          <option value="synthetic_daily_reports">synthetic_daily_reports</option>
        </select>
      </label>

      <label>
        <span>Granularity</span>
        <select value={options.granularity} onChange={(event) => updateOption('granularity', event.target.value)}>
          <option value="daily">daily</option>
          <option value="monthly">monthly</option>
        </select>
      </label>

      <label>
        <span>Period start</span>
        <input
          type="date"
          value={options.periodStart}
          onChange={(event) => updateOption('periodStart', event.target.value)}
        />
      </label>

      <label>
        <span>Period end</span>
        <input
          type="date"
          value={options.periodEnd}
          onChange={(event) => updateOption('periodEnd', event.target.value)}
        />
      </label>

      <label className="checkboxLabel">
        <input
          checked={options.isSynthetic}
          type="checkbox"
          onChange={(event) => updateOption('isSynthetic', event.target.checked)}
        />
        <span>Synthetic data</span>
      </label>
    </div>
  );
}
