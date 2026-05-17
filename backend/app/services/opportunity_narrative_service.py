from app.schemas.opportunity import OpportunityComponents


def priority_label(score: float) -> str:
    """Build priority label.
    Args:
        score (float): Opportunity score."""
    if score >= 0.75:
        return 'high'
    if score >= 0.55:
        return 'medium'
    if score >= 0.35:
        return 'low'
    return 'avoid'


def market_type(
    score: float,
    components: OpportunityComponents,
    active_competitors: int,
    paid_share: float | None,
) -> str:
    """Build market type.
    Args:
        score (float): Opportunity score.
        components (OpportunityComponents): Score components.
        active_competitors (int): Active competitor count.
        paid_share (float | None): Paid channel share."""
    if score >= 0.70 and (components.entry_difficulty_score or 0) < 0.50:
        return 'market_window'
    if (components.traffic_score or 0) >= 0.70 and (components.entry_difficulty_score or 0) >= 0.70:
        return 'protected'
    if (components.traffic_score or 0) >= 0.50 and active_competitors <= 3:
        return 'emerging'
    if (components.volatility_score or 0) < 0.40:
        return 'volatile'
    if active_competitors <= 3 and (components.quality_score or 0) >= 0.60:
        return 'low_noise'
    if active_competitors >= 10 and paid_share is not None and paid_share >= 0.35:
        return 'overheated'
    return 'unclear'


def strength_list(components: OpportunityComponents) -> list[str]:
    """Build strengths.
    Args:
        components (OpportunityComponents): Score components."""
    strengths = []
    if (components.traffic_score or 0) > 0.7:
        strengths.append('Strong confirmed competitor traffic.')
    if (components.competition_score or 0) > 0.65:
        strengths.append('Competition structure leaves room for entry.')
    if (components.quality_score or 0) > 0.7:
        strengths.append('Audience quality looks strong.')
    if (components.channel_gap_score or 0) > 0.65:
        strengths.append('Channel mix suggests acquisition opportunities.')
    if (components.localization_potential_score or 0) > 0.65:
        strengths.append('Localization may improve conversion and retention.')
    if not strengths:
        strengths.append('The market has enough signal for a cautious review.')
    return strengths


def risk_list(
    components: OpportunityComponents,
    leader_share: float | None,
    top_share: float | None,
    quality_status: str,
) -> list[str]:
    """Build risks.
    Args:
        components (OpportunityComponents): Score components.
        leader_share (float | None): Leader share.
        top_share (float | None): Top three share.
        quality_status (str): Data quality status."""
    risks = []
    if leader_share is not None and leader_share > 0.5:
        risks.append('A strong leader may make market entry harder.')
    if top_share is not None and top_share > 0.75:
        risks.append('Top competitors capture a large traffic share.')
    if (components.entry_difficulty_score or 0) > 0.7:
        risks.append('Entry difficulty is high.')
    if (components.volatility_score or 0) < 0.4:
        risks.append('The market looks volatile.')
    if (components.quality_score or 0) < 0.4:
        risks.append('Traffic quality may be weak.')
    if components.channel_gap_score is None:
        risks.append('Channel metrics are unavailable, so channel gap was excluded from scoring.')
    if quality_status == 'warning':
        risks.append('Latest data quality checks contain warnings.')
    if not risks:
        risks.append('No severe risk signal was detected in the current formula.')
    return risks


def explain_score(country_name: str, priority: str, components: OpportunityComponents, risks: list[str]) -> str:
    """Build score explanation.
    Args:
        country_name (str): Country name.
        priority (str): Recommended priority.
        components (OpportunityComponents): Score components.
        risks (list[str]): Risk list."""
    drivers = {
        'traffic demand': components.traffic_score or 0,
        'competition structure': components.competition_score or 0,
        'audience quality': components.quality_score or 0,
        'channel opportunity': components.channel_gap_score or 0,
        'localization potential': components.localization_potential_score or 0,
    }
    main_driver = max(drivers, key=drivers.get)
    main_risk = risks[0] if risks else 'No severe risk signal was detected.'
    explanation = (
        f'{country_name} receives a {priority} opportunity priority because {main_driver} is the strongest positive driver. '
        f'The main risk is: {main_risk} '
        f'This means the country should be evaluated with a focused entry strategy before larger budget allocation.'
    )
    return explanation
