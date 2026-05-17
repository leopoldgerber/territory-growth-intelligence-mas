from app.schemas.country import CountryItem, CountrySummaryMetrics


def percent_text(value: float | None) -> str:
    """Format percent text.
    Args:
        value (float | None): Ratio value."""
    if value is None:
        return 'n/a'
    text = f'{value * 100:.1f}%'
    return text


def number_text(value: float | None) -> str:
    """Format number text.
    Args:
        value (float | None): Number value."""
    if value is None:
        return '0'
    text = f'{value:,.0f}'
    return text


def build_summary(country: CountryItem, metrics: CountrySummaryMetrics) -> str:
    """Build country summary.
    Args:
        country (CountryItem): Country metadata.
        metrics (CountrySummaryMetrics): Summary metrics."""
    leader = metrics.leader_company or metrics.leader_domain or 'n/a'
    summary = (
        f'{country.country_name_en} has {metrics.active_competitors_count} active competitors in the selected period. '
        f'Total competitor traffic is {number_text(metrics.total_competitor_traffic)}. '
        f'The market leader is {leader} with {percent_text(metrics.leader_share)} of traffic. '
        f'Top-3 competitors concentrate {percent_text(metrics.top_3_share)} of traffic. '
        f'Desktop share is {percent_text(metrics.desktop_share)}, mobile share is {percent_text(metrics.mobile_share)}.'
    )
    return summary
