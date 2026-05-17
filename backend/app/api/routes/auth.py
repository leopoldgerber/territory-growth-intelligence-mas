from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse, UserInfo
from app.services.auth_service import login_user, logout_user, refresh_access, register_user, user_info
from app.services.permission_service import current_user


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse)
def post_register(request: RegisterRequest, session: Session = Depends(get_session)) -> TokenResponse:
    """Register user.
    Args:
        request (RegisterRequest): Register request.
        session (Session): Database session."""
    response = register_user(session, request)
    return response


@router.post('/login', response_model=TokenResponse)
def post_login(request: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    """Login user.
    Args:
        request (LoginRequest): Login request.
        session (Session): Database session."""
    response = login_user(session, request)
    return response


@router.post('/refresh', response_model=TokenResponse)
def post_refresh(request: RefreshRequest, session: Session = Depends(get_session)) -> TokenResponse:
    """Refresh token.
    Args:
        request (RefreshRequest): Refresh request.
        session (Session): Database session."""
    response = refresh_access(session, request.refresh_token)
    return response


@router.post('/logout')
def post_logout(request: LogoutRequest, session: Session = Depends(get_session)) -> dict[str, str]:
    """Logout user.
    Args:
        request (LogoutRequest): Logout request.
        session (Session): Database session."""
    response = logout_user(session, request.refresh_token)
    return response


@router.get('/me', response_model=UserInfo)
def get_me(user: dict[str, object] = Depends(current_user), session: Session = Depends(get_session)) -> UserInfo:
    """Get current user.
    Args:
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = user_info(session, user)
    return response
