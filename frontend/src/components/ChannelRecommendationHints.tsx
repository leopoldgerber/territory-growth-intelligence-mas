type ChannelRecommendationHintsProps = {
  hints: string[];
};

export function ChannelRecommendationHints({ hints }: ChannelRecommendationHintsProps) {
  return (
    <section className="overviewPanel" aria-label="Channel recommendation hints">
      <div className="sectionHeader">
        <div>
          <h2>Recommendation hints</h2>
          <p>Initial rule-based hints</p>
        </div>
      </div>
      <ul className="hintList">
        {hints.map((hint) => (
          <li key={hint}>{hint}</li>
        ))}
        {hints.length === 0 && <li>No channel hints for selected filters.</li>}
      </ul>
    </section>
  );
}
