from app.schemas.country import CountryMetricsResponse, CountrySummary


def number_text(value: float | int | None) -> str:
    """Format number text.
    Args:
        value (float | int | None): Source value."""
    if value is None:
        return 'n/a'
    text = f'{value:,.0f}'
    return text


def percent_text(value: float | None) -> str:
    """Format percent text.
    Args:
        value (float | None): Source value."""
    if value is None:
        return 'n/a'
    text = f'{value * 100:.1f}%'
    return text


def decimal_text(value: float | None) -> str:
    """Format decimal text.
    Args:
        value (float | None): Source value."""
    if value is None:
        return 'n/a'
    text = f'{value:.2f}'
    return text


def concentration_text(value: float | None) -> str:
    """Build concentration text.
    Args:
        value (float | None): HHI value."""
    if value is None:
        return 'Market concentration cannot be calculated from the available data.'
    if value < 0.15:
        return 'The market is fragmented, with no clear single dominant player.'
    if value <= 0.25:
        return 'The market is moderately concentrated.'
    return 'The market is highly concentrated.'


def engagement_text(value: float | None) -> str:
    """Build engagement text.
    Args:
        value (float | None): Engagement score."""
    if value is None:
        return 'Engagement score is not available.'
    if value < 0.4:
        return 'Audience quality looks weak.'
    if value < 0.7:
        return 'Audience quality looks moderate.'
    return 'Audience quality looks strong.'


def volatility_text(value: float | None) -> str:
    """Build volatility text.
    Args:
        value (float | None): Volatility score."""
    if value is None:
        return 'Volatility score is not available for this period.'
    if value < 0.3:
        return 'The market looks stable.'
    if value < 0.7:
        return 'The market shows moderate volatility.'
    return 'The market is volatile and may contain sharp traffic shifts.'


def risk_items(metrics: CountryMetricsResponse) -> list[str]:
    """Build risk items.
    Args:
        metrics (CountryMetricsResponse): Country metrics."""
    values = metrics.metrics
    risks = []
    if values.leader_share is not None and values.leader_share > 0.5:
        risks.append('The market is strongly controlled by the leader.')
    if values.top_3_share is not None and values.top_3_share > 0.75:
        risks.append('The top-3 competitors control a large traffic share.')
    if values.engagement_score is not None and values.engagement_score < 0.4:
        risks.append('Traffic quality appears weak based on engagement score.')
    if values.market_volatility_score is not None and values.market_volatility_score > 0.7:
        risks.append('The market is unstable and may require additional monitoring.')
    if metrics.calculation.data_quality_status == 'warning':
        risks.append('The dataset has data quality warnings.')
    if not risks:
        risks.append('No major rule-based risks were detected.')
    return risks


def recommendation_items(metrics: CountryMetricsResponse, channels: list[dict[str, object]]) -> list[str]:
    """Build recommendation items.
    Args:
        metrics (CountryMetricsResponse): Country metrics.
        channels (list[dict[str, object]]): Channel rows."""
    recommendations = [
        'Review this country for deeper opportunity scoring before budget decisions.',
        'Check localization potential and landing page fit for the leading traffic devices.',
    ]
    if channels:
        dominant_channel = channels[0].get('channel_name') or channels[0].get('channel_code')
        recommendations.append(f'Inspect {dominant_channel} as the current dominant channel.')
    if metrics.metrics.leader and metrics.metrics.leader.domain:
        recommendations.append(f'Study weak points of the leader: {metrics.metrics.leader.domain}.')
    recommendations.append('Do not make final budget decisions before the budget strategy stage.')
    return recommendations


def report_json(
    summary: CountrySummary,
    metrics: CountryMetricsResponse,
    channels: list[dict[str, object]],
) -> dict[str, object]:
    """Build report JSON.
    Args:
        summary (CountrySummary): Country summary.
        metrics (CountryMetricsResponse): Country metrics.
        channels (list[dict[str, object]]): Channel rows."""
    json_data = {
        'executive_summary': {
            'title': 'Executive summary',
            'items': [
                summary.generated_summary,
                concentration_text(metrics.metrics.market_concentration_hhi),
                engagement_text(metrics.metrics.engagement_score),
                volatility_text(metrics.metrics.market_volatility_score),
            ],
        },
        'market_overview': metrics.metrics.model_dump(),
        'top_competitors': [competitor.model_dump() for competitor in summary.top_competitors],
        'traffic_quality': {
            'avg_bounce_rate': metrics.metrics.avg_bounce_rate,
            'no_bounce_share': metrics.metrics.no_bounce_share,
            'engagement_score': metrics.metrics.engagement_score,
        },
        'channels': {'items': channels},
        'risks': risk_items(metrics),
        'initial_recommendations': recommendation_items(metrics, channels),
    }
    return json_data


def markdown_report(
    summary: CountrySummary,
    metrics: CountryMetricsResponse,
    channels: list[dict[str, object]],
) -> str:
    """Build Markdown report.
    Args:
        summary (CountrySummary): Country summary.
        metrics (CountryMetricsResponse): Country metrics.
        channels (list[dict[str, object]]): Channel rows."""
    country_name = summary.country.country_name_en
    period = f'{summary.period.date_from} - {summary.period.date_to}'
    competitor_lines = [
        '| Rank | Company | Domain | Traffic | Share | Bounce | No-bounce |',
        '|---:|---|---|---:|---:|---:|---:|',
    ]
    for competitor in summary.top_competitors:
        competitor_lines.append(
            '| '
            f'{competitor.rank} | {competitor.company_name or "n/a"} | {competitor.domain} | '
            f'{number_text(competitor.traffic)} | {percent_text(competitor.traffic_share)} | '
            f'{percent_text(competitor.bounce_rate)} | {number_text(competitor.traffic_no_bounce)} |'
        )
    channel_lines = ['| Channel | Traffic | Share |', '|---|---:|---:|']
    for channel in channels:
        channel_lines.append(
            f'| {channel.get("channel_name") or channel.get("channel_code")} | '
            f'{number_text(channel.get("traffic"))} | {percent_text(channel.get("traffic_share"))} |'
        )
    if not channels:
        channel_lines.append('| Channel analysis | n/a | n/a |')
    warning = ''
    if metrics.calculation.data_quality_status == 'warning':
        warning = '\n## Data quality warning\nThe dataset contains quality warnings. Interpret conclusions with caution.\n'
    markdown = f"""# Country Report: {country_name}

## Period
{period}
{warning}
## 1. Executive summary
- {summary.generated_summary}
- {concentration_text(metrics.metrics.market_concentration_hhi)}
- {engagement_text(metrics.metrics.engagement_score)}
- {volatility_text(metrics.metrics.market_volatility_score)}

## 2. Market overview
- Total competitor traffic: {number_text(metrics.metrics.total_competitor_traffic)}
- Active competitors: {metrics.metrics.active_competitors_count}
- Market leader: {metrics.metrics.leader.company_name if metrics.metrics.leader else 'n/a'}
- Leader share: {percent_text(metrics.metrics.leader_share)}
- Top-3 share: {percent_text(metrics.metrics.top_3_share)}
- HHI: {decimal_text(metrics.metrics.market_concentration_hhi)}

## 3. Top competitors
{chr(10).join(competitor_lines)}

## 4. Traffic quality
- Average bounce rate: {percent_text(metrics.metrics.avg_bounce_rate)}
- No-bounce share: {percent_text(metrics.metrics.no_bounce_share)}
- Pages per visit: {decimal_text(metrics.metrics.avg_pages_per_visit)}
- Average duration seconds: {decimal_text(metrics.metrics.avg_visit_duration_seconds)}
- Engagement score: {decimal_text(metrics.metrics.engagement_score)}

## 5. Device structure
- Desktop share: {percent_text(metrics.metrics.desktop_share)}
- Mobile share: {percent_text(metrics.metrics.mobile_share)}

## 6. Channels
{chr(10).join(channel_lines)}

## 7. Key risks
{chr(10).join([f'- {risk}' for risk in risk_items(metrics)])}

## 8. Initial strategic recommendations
{chr(10).join([f'- {recommendation}' for recommendation in recommendation_items(metrics, channels)])}
"""
    return markdown
