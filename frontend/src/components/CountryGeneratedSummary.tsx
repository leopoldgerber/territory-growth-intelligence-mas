type CountryGeneratedSummaryProps = {
  text: string;
};

export function CountryGeneratedSummary({ text }: CountryGeneratedSummaryProps) {
  return (
    <section className="overviewPanel" aria-label="Generated summary">
      <div className="sectionHeader">
        <div>
          <h2>Generated summary</h2>
          <p>Rule-based interpretation</p>
        </div>
      </div>
      <p className="generatedSummary">{text}</p>
    </section>
  );
}
