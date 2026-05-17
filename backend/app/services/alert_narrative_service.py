HINTS = {
    'traffic_spike': 'Review whether the growth is connected to a new campaign, channel change, or market entry.',
    'traffic_drop': 'Check whether the competitor is losing position or ending a campaign in this market.',
    'market_traffic_spike': 'Review whether the market is entering a higher demand window.',
    'market_traffic_drop': 'Check whether market demand is weakening or source data changed.',
    'new_market_signal': 'Monitor this country closely and review competitor channels to understand the entry path.',
    'abandoned_market_signal': 'Evaluate whether this creates an opportunity to test the country with lower competitive pressure.',
    'leader_changed': 'Market shares may be shifting; review whether a challenger is gaining sustainable traction.',
    'paid_spike': 'Investigate whether competitors are validating demand through paid campaigns.',
    'referral_spike': 'Review journey sources and partner/referral opportunities.',
    'social_spike': 'Review whether competitors are testing localized social positioning.',
    'channel_shift': 'Review channel mix to understand whether acquisition strategy changed.',
    'quality_drop': 'Traffic volume may be growing at the expense of quality; avoid treating this as healthy growth without further checks.',
    'bounce_spike': 'Check whether traffic quality or landing relevance deteriorated.',
    'no_bounce_drop': 'Review whether useful traffic is declining in the selected market.',
    'challenger_growth': 'Review whether a challenger is gaining sustainable traction.',
    'leader_weakening': 'Review whether the leader is losing share to challengers.',
}


def recommendation_hint(event_type: str) -> str:
    """Build recommendation hint.
    Args:
        event_type (str): Alert event type."""
    hint = HINTS.get(event_type, 'Review the evidence and compare related market, channel, and competitor signals.')
    return hint


def entity_label(row: dict[str, object]) -> str:
    """Build entity label.
    Args:
        row (dict[str, object]): Alert source row."""
    domain = row.get('domain')
    country = row.get('country_name_en')
    channel = row.get('channel_name')
    values = [str(value) for value in [domain, country, channel] if value]
    label = ' / '.join(values) if values else 'Selected scope'
    return label


def title_text(event_type: str, row: dict[str, object]) -> str:
    """Build alert title.
    Args:
        event_type (str): Alert event type.
        row (dict[str, object]): Alert source row."""
    label = entity_label(row)
    titles = {
        'traffic_spike': f'{label} traffic increased sharply',
        'traffic_drop': f'{label} traffic dropped sharply',
        'market_traffic_spike': f'{label} market traffic increased sharply',
        'market_traffic_drop': f'{label} market traffic dropped sharply',
        'new_market_signal': f'{label} appeared in a new market',
        'abandoned_market_signal': f'{label} nearly disappeared from a market',
        'leader_changed': f'{label} market leader changed',
        'paid_spike': f'{label} paid traffic increased sharply',
        'referral_spike': f'{label} referral traffic increased sharply',
        'social_spike': f'{label} social traffic increased sharply',
        'channel_shift': f'{label} channel mix shifted',
        'quality_drop': f'{label} traffic quality deteriorated',
        'bounce_spike': f'{label} bounce traffic increased',
        'no_bounce_drop': f'{label} no-bounce traffic decreased',
        'challenger_growth': f'{label} challenger gained share',
        'leader_weakening': f'{label} leader share weakened',
    }
    title = titles.get(event_type, f'{label} changed')
    return title


def description_text(event_type: str, row: dict[str, object]) -> str:
    """Build alert description.
    Args:
        event_type (str): Alert event type.
        row (dict[str, object]): Alert source row."""
    previous_value = float(row.get('previous_value') or row.get('baseline_value') or 0)
    current_value = float(row.get('current_value') or 0)
    absolute_change = current_value - previous_value
    description = (
        f'{event_type} was detected because the selected metric changed '
        f'from {round(previous_value, 4)} to {round(current_value, 4)} '
        f'with absolute change {round(absolute_change, 4)}.'
    )
    return description
