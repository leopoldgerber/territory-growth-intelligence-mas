type GenerateCountryReportButtonProps = {
  disabled: boolean;
  isGenerating: boolean;
  onGenerate: () => void;
};

export function GenerateCountryReportButton({
  disabled,
  isGenerating,
  onGenerate,
}: GenerateCountryReportButtonProps) {
  return (
    <button type="button" onClick={onGenerate} disabled={disabled || isGenerating}>
      {isGenerating ? 'Generating report' : 'Generate Country Report'}
    </button>
  );
}
