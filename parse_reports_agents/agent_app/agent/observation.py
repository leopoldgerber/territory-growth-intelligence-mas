from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Observation:
    url: str = ''
    title: str = ''
    active_domain: str = ''
    active_section: str = ''
    active_tab: str = ''
    selected_month: str = ''
    visible_text: str = ''
    evidence: dict[str, Any] = field(default_factory=dict)


def empty_observation() -> Observation:
    """Create empty observation.
    Args:
        None (None): No arguments are required."""
    observation = Observation()
    return observation


def observe_page(page: Any) -> Observation:
    """Observe current page.
    Args:
        page (Any): Playwright page."""
    title = ''
    visible_text = ''
    try:
        title = page.title()
    except Exception:
        title = ''
    try:
        visible_text = page.locator('body').inner_text(timeout=1000)[:5000]
    except Exception:
        visible_text = ''
    observation = Observation(
        url=getattr(page, 'url', ''),
        title=title,
        visible_text=visible_text,
    )
    return observation


def observation_dict(observation: Observation) -> dict[str, Any]:
    """Convert observation to dictionary.
    Args:
        observation (Observation): Page observation."""
    data = asdict(observation)
    return data
