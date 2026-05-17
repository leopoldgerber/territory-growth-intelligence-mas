from app.schemas.competitor import CompetitorItem, CompetitorSummaryMetrics


def build_summary(competitor: CompetitorItem, metrics: CompetitorSummaryMetrics) -> str:
    """Build competitor summary.
    Args:
        competitor (CompetitorItem): Competitor metadata.
        metrics (CompetitorSummaryMetrics): Competitor metrics."""
    top_country = metrics.top_country or 'n/a'
    top_share = 'n/a' if metrics.top_country_share is None else f'{metrics.top_country_share * 100:.1f}%'
    summary = (
        f'{competitor.company_name or competitor.domain} is active in {metrics.active_countries_count} countries. '
        f'{top_country} is its strongest country with {top_share} of total country-level traffic. '
        f'Total traffic in the selected period is {metrics.total_traffic:,.0f}.'
    )
    return summary
