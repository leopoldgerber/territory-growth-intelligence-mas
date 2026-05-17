from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.project import (
    ProjectCompetitorCreate,
    ProjectCompetitorItem,
    ProjectCompetitorList,
    ProjectCountryCreate,
    ProjectCountryItem,
    ProjectCountryList,
    ProjectCountryUpdate,
    ProjectCreate,
    ProjectItem,
    ProjectList,
    ProjectMemberCreate,
    ProjectMemberItem,
    ProjectMemberList,
    ProjectMemberUpdate,
    ProjectUpdate,
)
from app.services.permission_service import require_project_role


ROLES = ['admin', 'analyst', 'viewer']


def normalize_slug(value: str) -> str:
    """Normalize project slug.
    Args:
        value (str): Source slug."""
    slug = value.strip().lower().replace(' ', '-')
    return slug


def validate_role(role: str) -> str:
    """Validate project role.
    Args:
        role (str): Project role."""
    if role not in ROLES:
        raise HTTPException(status_code=400, detail='Project role is invalid.')
    return role


def list_projects(session: Session, user: dict[str, object]) -> ProjectList:
    """List user projects.
    Args:
        session (Session): Database session.
        user (dict[str, object]): Current user."""
    if bool(user.get('is_superadmin')):
        query = """
            SELECT projects.*, 'admin' AS role, COUNT(*) OVER() AS total
            FROM projects
            WHERE projects.status != 'archived'
            ORDER BY projects.project_name
        """
        params = {}
    else:
        query = """
            SELECT projects.*, members.role, COUNT(*) OVER() AS total
            FROM project_members AS members
            JOIN projects ON projects.project_id = members.project_id
            WHERE members.user_id = :user_id
              AND members.status = 'active'
              AND projects.status != 'archived'
            ORDER BY projects.project_name
        """
        params = {'user_id': user['user_id']}
    rows = [dict(row._mapping) for row in session.execute(text(query), params)]
    total = int(rows[0]['total']) if rows else 0
    items = [ProjectItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return ProjectList(items=items, total=total)


def create_project(session: Session, request: ProjectCreate, user: dict[str, object]) -> ProjectItem:
    """Create project.
    Args:
        session (Session): Database session.
        request (ProjectCreate): Project request.
        user (dict[str, object]): Current user."""
    slug = normalize_slug(request.project_slug)
    result = session.execute(
        text(
            """
            INSERT INTO projects (
                project_name, project_slug, description, own_company_id,
                default_currency_code, created_by_user_id
            )
            VALUES (
                :project_name, :project_slug, :description, :own_company_id,
                :default_currency_code, :created_by_user_id
            )
            RETURNING *
            """,
        ),
        {
            'project_name': request.project_name,
            'project_slug': slug,
            'description': request.description,
            'own_company_id': request.own_company_id,
            'default_currency_code': request.default_currency_code[:3].upper(),
            'created_by_user_id': user['user_id'],
        },
    )
    project = dict(result.first()._mapping)
    session.execute(
        text(
            """
            INSERT INTO project_members (project_id, user_id, role, status)
            VALUES (:project_id, :user_id, 'admin', 'active')
            """,
        ),
        {'project_id': project['project_id'], 'user_id': user['user_id']},
    )
    session.commit()
    project['role'] = 'admin'
    item = ProjectItem(**project)
    return item


def get_project(session: Session, project_id: int, user: dict[str, object]) -> ProjectItem:
    """Get project.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        user (dict[str, object]): Current user."""
    role = require_project_role(session, user, project_id, ROLES)
    row = session.execute(text('SELECT * FROM projects WHERE project_id = :project_id'), {'project_id': project_id}).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Project not found.')
    project = dict(row._mapping)
    project['role'] = role
    item = ProjectItem(**project)
    return item


def update_project(session: Session, project_id: int, request: ProjectUpdate, user: dict[str, object]) -> ProjectItem:
    """Update project.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (ProjectUpdate): Project update.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin'])
    current = get_project(session, project_id, user)
    payload = request.model_dump(exclude_unset=True)
    params = {
        'project_id': project_id,
        'project_name': payload.get('project_name', current.project_name),
        'description': payload.get('description', current.description),
        'own_company_id': payload.get('own_company_id', current.own_company_id),
        'default_currency_code': payload.get('default_currency_code', current.default_currency_code)[:3].upper(),
        'status': payload.get('status', current.status),
    }
    row = session.execute(
        text(
            """
            UPDATE projects
            SET project_name = :project_name,
                description = :description,
                own_company_id = :own_company_id,
                default_currency_code = :default_currency_code,
                status = :status,
                updated_at = now()
            WHERE project_id = :project_id
            RETURNING *
            """,
        ),
        params,
    ).first()
    session.commit()
    project = dict(row._mapping)
    project['role'] = 'admin'
    item = ProjectItem(**project)
    return item


def list_members(session: Session, project_id: int, user: dict[str, object]) -> ProjectMemberList:
    """List project members.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ROLES)
    rows = session.execute(
        text(
            """
            SELECT users.user_id, users.email, users.full_name, members.role, members.status, COUNT(*) OVER() AS total
            FROM project_members AS members
            JOIN users ON users.user_id = members.user_id
            WHERE members.project_id = :project_id
            ORDER BY users.email
            """,
        ),
        {'project_id': project_id},
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [ProjectMemberItem(**{key: value for key, value in row.items() if key != 'total'}) for row in data]
    return ProjectMemberList(items=items, total=total)


def add_member(session: Session, project_id: int, request: ProjectMemberCreate, user: dict[str, object]) -> ProjectMemberItem:
    """Add project member.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (ProjectMemberCreate): Member request.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin'])
    validate_role(request.role)
    row = session.execute(text('SELECT * FROM users WHERE lower(email) = lower(:email)'), {'email': request.email}).first()
    if row is None:
        raise HTTPException(status_code=404, detail='User email is not registered.')
    member_user = dict(row._mapping)
    session.execute(
        text(
            """
            INSERT INTO project_members (project_id, user_id, role, status)
            VALUES (:project_id, :user_id, :role, 'active')
            ON CONFLICT (project_id, user_id)
            DO UPDATE SET role = EXCLUDED.role, status = 'active', updated_at = now()
            """,
        ),
        {'project_id': project_id, 'user_id': member_user['user_id'], 'role': request.role},
    )
    session.commit()
    item = ProjectMemberItem(
        user_id=int(member_user['user_id']),
        email=str(member_user['email']),
        full_name=member_user.get('full_name'),
        role=request.role,
        status='active',
    )
    return item


def update_member(
    session: Session,
    project_id: int,
    member_user_id: int,
    request: ProjectMemberUpdate,
    user: dict[str, object],
) -> ProjectMemberItem:
    """Update project member.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        member_user_id (int): Member user identifier.
        request (ProjectMemberUpdate): Member update.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin'])
    role = validate_role(request.role) if request.role is not None else None
    row = session.execute(
        text(
            """
            UPDATE project_members
            SET role = COALESCE(:role, role),
                status = COALESCE(:status, status),
                updated_at = now()
            WHERE project_id = :project_id AND user_id = :user_id
            RETURNING user_id, role, status
            """,
        ),
        {
            'project_id': project_id,
            'user_id': member_user_id,
            'role': role,
            'status': request.status,
        },
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Project member not found.')
    user_row = session.execute(text('SELECT email, full_name FROM users WHERE user_id = :user_id'), {'user_id': member_user_id}).first()
    session.commit()
    member = dict(row._mapping)
    member.update(dict(user_row._mapping))
    item = ProjectMemberItem(**member)
    return item


def list_competitors(session: Session, project_id: int, user: dict[str, object]) -> ProjectCompetitorList:
    """List project competitors.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ROLES)
    rows = session.execute(
        text(
            """
            SELECT
                competitors.domain_id,
                domains.domain,
                competitors.company_id,
                companies.company_name,
                competitors.competitor_tier,
                competitors.priority,
                competitors.notes,
                competitors.is_active,
                COUNT(*) OVER() AS total
            FROM project_competitors AS competitors
            LEFT JOIN dim_domain AS domains ON domains.domain_id = competitors.domain_id
            LEFT JOIN dim_company AS companies ON companies.company_id = competitors.company_id
            WHERE competitors.project_id = :project_id
            ORDER BY competitors.is_active DESC, competitors.priority, domains.domain
            """,
        ),
        {'project_id': project_id},
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [ProjectCompetitorItem(**{key: value for key, value in row.items() if key != 'total'}) for row in data]
    return ProjectCompetitorList(items=items, total=total)


def add_competitor(
    session: Session,
    project_id: int,
    request: ProjectCompetitorCreate,
    user: dict[str, object],
) -> ProjectCompetitorItem:
    """Add project competitor.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (ProjectCompetitorCreate): Competitor request.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin', 'analyst'])
    session.execute(
        text(
            """
            INSERT INTO project_competitors (
                project_id, company_id, domain_id, competitor_tier, priority, notes, is_active
            )
            VALUES (
                :project_id, :company_id, :domain_id, :competitor_tier, :priority, :notes, true
            )
            ON CONFLICT (project_id, domain_id)
            DO UPDATE SET
                company_id = EXCLUDED.company_id,
                competitor_tier = EXCLUDED.competitor_tier,
                priority = EXCLUDED.priority,
                notes = EXCLUDED.notes,
                is_active = true,
                updated_at = now()
            """,
        ),
        {'project_id': project_id, **request.model_dump()},
    )
    session.commit()
    competitors = list_competitors(session, project_id, user)
    item = next(item for item in competitors.items if item.domain_id == request.domain_id)
    return item


def remove_competitor(session: Session, project_id: int, domain_id: int, user: dict[str, object]) -> dict[str, object]:
    """Remove project competitor.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        domain_id (int): Domain identifier.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin', 'analyst'])
    session.execute(
        text(
            """
            UPDATE project_competitors
            SET is_active = false, updated_at = now()
            WHERE project_id = :project_id AND domain_id = :domain_id
            """,
        ),
        {'project_id': project_id, 'domain_id': domain_id},
    )
    session.commit()
    return {'project_id': project_id, 'domain_id': domain_id, 'status': 'inactive'}


def list_target_countries(session: Session, project_id: int, user: dict[str, object]) -> ProjectCountryList:
    """List target countries.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ROLES)
    rows = session.execute(
        text(
            """
            SELECT
                targets.country_id,
                countries.country_name_en,
                countries.country_name_ru,
                countries.region_name_en,
                targets.status,
                targets.strategic_priority,
                targets.notes,
                COUNT(*) OVER() AS total
            FROM project_target_countries AS targets
            JOIN dim_country AS countries ON countries.country_id = targets.country_id
            WHERE targets.project_id = :project_id
            ORDER BY targets.strategic_priority, countries.country_name_en
            """,
        ),
        {'project_id': project_id},
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [ProjectCountryItem(**{key: value for key, value in row.items() if key != 'total'}) for row in data]
    return ProjectCountryList(items=items, total=total)


def add_target_country(
    session: Session,
    project_id: int,
    request: ProjectCountryCreate,
    user: dict[str, object],
) -> ProjectCountryItem:
    """Add target country.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (ProjectCountryCreate): Target country request.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin', 'analyst'])
    session.execute(
        text(
            """
            INSERT INTO project_target_countries (project_id, country_id, status, strategic_priority, notes)
            VALUES (:project_id, :country_id, :status, :strategic_priority, :notes)
            ON CONFLICT (project_id, country_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                strategic_priority = EXCLUDED.strategic_priority,
                notes = EXCLUDED.notes,
                updated_at = now()
            """,
        ),
        {'project_id': project_id, **request.model_dump()},
    )
    session.commit()
    countries = list_target_countries(session, project_id, user)
    item = next(item for item in countries.items if item.country_id == request.country_id)
    return item


def update_target_country(
    session: Session,
    project_id: int,
    country_id: int,
    request: ProjectCountryUpdate,
    user: dict[str, object],
) -> ProjectCountryItem:
    """Update target country.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        request (ProjectCountryUpdate): Target country update.
        user (dict[str, object]): Current user."""
    require_project_role(session, user, project_id, ['admin', 'analyst'])
    row = session.execute(
        text(
            """
            UPDATE project_target_countries
            SET status = COALESCE(:status, status),
                strategic_priority = COALESCE(:strategic_priority, strategic_priority),
                notes = COALESCE(:notes, notes),
                updated_at = now()
            WHERE project_id = :project_id AND country_id = :country_id
            RETURNING country_id, status, strategic_priority, notes
            """,
        ),
        {
            'project_id': project_id,
            'country_id': country_id,
            'status': request.status,
            'strategic_priority': request.strategic_priority,
            'notes': request.notes,
        },
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Target country not found.')
    session.commit()
    countries = list_target_countries(session, project_id, user)
    item = next(item for item in countries.items if item.country_id == int(row._mapping['country_id']))
    return item
