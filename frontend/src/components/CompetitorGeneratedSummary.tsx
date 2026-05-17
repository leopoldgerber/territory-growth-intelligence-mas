type CompetitorGeneratedSummaryProps = {
  text: string;
};

export function CompetitorGeneratedSummary({ text }: CompetitorGeneratedSummaryProps) {
  return (
    <section className="overviewPanel" aria-label="Competitor generated summary">
      <div className="sectionHeader">
        <div>
          <h2>Competitor summary</h2>
          <p>Rule-based interpretation</p>
        </div>
      </div>
      <p className="generatedSummary">{text}</p>
    </section>
  );
}
