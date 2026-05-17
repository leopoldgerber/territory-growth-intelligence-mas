from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.services.auth_service import get_user, verify_token


security = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Get current user.
    Args:
        credentials (HTTPAuthorizationCredentials | None): Bearer credentials.
        session (Session): Database session."""
    if credentials is None:
        raise HTTPException(status_code=401, detail='Authentication required.')
    payload = verify_token(credentials.credentials, 'access')
    user = get_user(session, int(payload['sub']))
    if user is None or user['status'] != 'active':
        raise HTTPException(status_code=401, detail='User is not active.')
    return user


def project_role(session: Session, user_id: int, project_id: int) -> str | None:
    """Get project role.
    Args:
        session (Session): Database session.
        user_id (int): User identifier.
        project_id (int): Project identifier."""
    row = session.execute(
        text(
            """
            SELECT role
            FROM project_members
            WHERE user_id = :user_id
              AND project_id = :project_id
              AND status = 'active'
            """,
        ),
        {'user_id': user_id, 'project_id': project_id},
    ).first()
    role = str(row._mapping['role']) if row else None
    return role


def require_project_role(
    session: Session,
    user: dict[str, object],
    project_id: int,
    allowed_roles: list[str],
) -> str:
    """Require project role.
    Args:
        session (Session): Database session.
        user (dict[str, object]): Current user.
        project_id (int): Project identifier.
        allowed_roles (list[str]): Allowed roles."""
    if bool(user.get('is_superadmin')):
        return 'admin'
    role = project_role(session, int(user['user_id']), project_id)
    if role is None:
        raise HTTPException(status_code=403, detail='Project access is forbidden.')
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail='Project role is not allowed.')
    return role
