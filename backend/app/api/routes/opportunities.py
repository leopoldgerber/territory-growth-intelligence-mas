from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.opportunity import OpportunityCountryList
from app.services.opportunity_scoring_service import list_scores


router = APIRouter(prefix='/opportunities', tags=['opportunities'])


@router.get('/countries', response_model=OpportunityCountryList)
def get_countries(
    date_from: date,
    date_to: date,
    region_id: int | None = None,
    priority: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    calculate_if_missing: bool = True,
    force_recalculate: bool = False,
    recalculate_if_missing: bool | None = None,
    session: Session = Depends(get_session),
) -> OpportunityCountryList:
    """Get opportunity countries.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date.
        region_id (int | None): Region identifier.
        priority (str | None): Priority filter.
        limit (int): Result limit.
        offset (int): Result offset.
        calculate_if_missing (bool): Calculate missing scores flag.
        force_recalculate (bool): Force recalculation flag.
        recalculate_if_missing (bool | None): Legacy calculate missing scores flag.
        session (Session): Database session."""
    resolved_calculate = calculate_if_missing if recalculate_if_missing is None else recalculate_if_missing
    result = list_scores(
        session,
        date_from,
        date_to,
        region_id,
        priority,
        limit,
        offset,
        resolved_calculate,
        force_recalculate,
    )
    return result
