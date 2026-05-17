from app.schemas.competitor import CompetitorSignalSet


def build_signals(items: list[dict[str, object]]) -> CompetitorSignalSet:
    """Build competitor signals.
    Args:
        items (list[dict[str, object]]): Country items."""
    anchor = [item for item in items if item.get('country_role') == 'anchor']
    peripheral = [item for item in items if item.get('country_role') == 'peripheral']
    growing = [item for item in items if item.get('signal') == 'growing']
    declining = [item for item in items if item.get('signal') == 'declining']
    new_markets = [item for item in items if item.get('signal') == 'new']
    abandoned = [item for item in items if item.get('signal') == 'abandoned']
    signals = CompetitorSignalSet(
        anchor_countries=anchor[:10],
        peripheral_countries=peripheral[:10],
        growing_countries=growing[:10],
        declining_countries=declining[:10],
        new_market_signals=new_markets[:10],
        abandoned_market_signals=abandoned[:10],
    )
    return signals
