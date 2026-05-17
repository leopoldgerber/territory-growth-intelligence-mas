from app.schemas.advanced_strategy import AdvancedAllocationItem, AdvancedScoreValues


ALLOCATIONS = {
    'seo_plus_paid_validation': {
        'paid_search': 0.35,
        'seo_content': 0.30,
        'localization': 0.15,
        'referral_partnerships': 0.10,
        'creative_testing': 0.05,
        'market_research': 0.05,
    },
    'paid_fast_validation': {
        'paid_search': 0.50,
        'landing_page_optimization': 0.15,
        'creative_testing': 0.15,
        'localization': 0.10,
        'seo_content': 0.05,
        'market_research': 0.05,
    },
    'localization_first': {
        'localization': 0.30,
        'landing_page_optimization': 0.25,
        'paid_search': 0.20,
        'seo_content': 0.15,
        'creative_testing': 0.05,
        'market_research': 0.05,
    },
    'content_led_entry': {
        'seo_content': 0.45,
        'localization': 0.20,
        'paid_search': 0.15,
        'referral_partnerships': 0.10,
        'market_research': 0.10,
    },
    'referral_partnership_entry': {
        'referral_partnerships': 0.35,
        'seo_content': 0.25,
        'localization': 0.15,
        'paid_search': 0.15,
        'market_research': 0.10,
    },
    'aggressive_growth_push': {
        'paid_search': 0.40,
        'seo_content': 0.25,
        'localization': 0.15,
        'creative_testing': 0.10,
        'referral_partnerships': 0.10,
    },
    'defensive_monitoring': {
        'market_research': 0.30,
        'landing_page_optimization': 0.25,
        'seo_content': 0.20,
        'paid_search': 0.15,
        'creative_testing': 0.10,
    },
    'avoid_or_wait': {
        'market_research': 0.45,
        'landing_page_optimization': 0.25,
        'localization': 0.20,
        'creative_testing': 0.10,
    },
}


def category_rationale(category: str, scores: AdvancedScoreValues) -> str:
    """Build rationale.
    Args:
        category (str): Allocation category.
        scores (AdvancedScoreValues): Advanced scores."""
    mapping = {
        'paid_search': 'Paid search validates demand quickly and produces measurable CAC evidence.',
        'seo_content': 'SEO content compounds organic demand and reduces paid dependency over time.',
        'referral_partnerships': 'Referral partnerships use backlink and PR signals to build authority.',
        'social_testing': 'Social testing checks message resonance with limited spend.',
        'localization': 'Localization improves fit where audience and UX signals need adaptation.',
        'creative_testing': 'Creative testing improves paid and landing-page conversion quality.',
        'landing_page_optimization': 'Landing-page work protects conversion rates before scaling spend.',
        'market_research': 'Market research reduces uncertainty before larger commitments.',
    }
    rationale = mapping.get(category, 'Allocation supports the selected growth scenario.')
    if (scores.competitor_threat_score or 0) > 0.7 and category == 'paid_search':
        rationale = 'Paid search should be constrained because competitor threat is high.'
    return rationale


def risk_level(category: str, scores: AdvancedScoreValues) -> str:
    """Build risk level.
    Args:
        category (str): Allocation category.
        scores (AdvancedScoreValues): Advanced scores."""
    if category == 'paid_search' and (scores.paid_dependency_score or 0) > 0.65:
        return 'high'
    if (scores.competitor_threat_score or 0) > 0.75:
        return 'high'
    if category in ['market_research', 'landing_page_optimization']:
        return 'low'
    return 'medium'


def success_metric(category: str) -> str:
    """Build success metric.
    Args:
        category (str): Allocation category."""
    mapping = {
        'paid_search': 'CAC and qualified lead volume',
        'seo_content': 'Organic keyword growth and assisted leads',
        'referral_partnerships': 'Referring domains and referral visits',
        'social_testing': 'CTR and message engagement',
        'localization': 'Localized conversion rate',
        'creative_testing': 'CTR and landing-page conversion lift',
        'landing_page_optimization': 'Visit-to-lead rate',
        'market_research': 'Validated go/no-go decision',
    }
    metric = mapping.get(category, 'Scenario contribution')
    return metric


def allocate_advanced(
    strategy_name: str,
    budget_amount: float,
    expected_traffic: float,
    expected_leads: float,
    expected_clients: float,
    expected_revenue: float,
    scores: AdvancedScoreValues,
) -> list[AdvancedAllocationItem]:
    """Allocate advanced budget.
    Args:
        strategy_name (str): Strategy name.
        budget_amount (float): Budget amount.
        expected_traffic (float): Expected traffic.
        expected_leads (float): Expected leads.
        expected_clients (float): Expected clients.
        expected_revenue (float): Expected revenue.
        scores (AdvancedScoreValues): Advanced scores."""
    shares = ALLOCATIONS.get(strategy_name, ALLOCATIONS['seo_plus_paid_validation'])
    items = []
    for category, share in shares.items():
        item_budget = budget_amount * share
        item_clients = expected_clients * share
        items.append(
            AdvancedAllocationItem(
                allocation_category=category,
                budget_share=share,
                budget_amount=round(item_budget, 2),
                expected_traffic=round(expected_traffic * share, 2),
                expected_leads=round(expected_leads * share, 2),
                expected_clients=round(item_clients, 2),
                expected_revenue=round(expected_revenue * share, 2),
                estimated_cac=round(item_budget / item_clients, 2) if item_clients > 0 else None,
                rationale=category_rationale(category, scores),
                risk_level=risk_level(category, scores),
                success_metric=success_metric(category),
            ),
        )
    return items
