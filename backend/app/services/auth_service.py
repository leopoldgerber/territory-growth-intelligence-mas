import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.auth import LoginRequest, ProjectAccess, RegisterRequest, TokenResponse, UserInfo


HASH_ITERATIONS = 210000


def b64_encode(data: bytes) -> str:
    """Encode url-safe base64.
    Args:
        data (bytes): Binary data."""
    encoded = base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
    return encoded


def b64_decode(value: str) -> bytes:
    """Decode url-safe base64.
    Args:
        value (str): Encoded value."""
    padding = '=' * (-len(value) % 4)
    decoded = base64.urlsafe_b64decode((value + padding).encode('utf-8'))
    return decoded


def hash_password(password: str) -> str:
    """Hash user password.
    Args:
        password (str): Plain password."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, HASH_ITERATIONS)
    password_hash = f'pbkdf2_sha256${HASH_ITERATIONS}${b64_encode(salt)}${b64_encode(key)}'
    return password_hash


def verify_password(password: str, password_hash: str) -> bool:
    """Verify user password.
    Args:
        password (str): Plain password.
        password_hash (str): Stored password hash."""
    parts = password_hash.split('$')
    if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
        return False
    iterations = int(parts[1])
    salt = b64_decode(parts[2])
    expected_key = b64_decode(parts[3])
    actual_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    is_valid = hmac.compare_digest(actual_key, expected_key)
    return is_valid


def hash_token(token: str) -> str:
    """Hash refresh token.
    Args:
        token (str): Refresh token."""
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    return token_hash


def sign_payload(payload: dict[str, object]) -> str:
    """Sign token payload.
    Args:
        payload (dict[str, object]): Token payload."""
    settings = get_settings()
    payload_text = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    payload_part = b64_encode(payload_text.encode('utf-8'))
    signature = hmac.new(settings.auth_secret_key.encode('utf-8'), payload_part.encode('utf-8'), hashlib.sha256).digest()
    token = f'{payload_part}.{b64_encode(signature)}'
    return token


def verify_token(token: str, token_type: str) -> dict[str, object]:
    """Verify signed token.
    Args:
        token (str): Signed token.
        token_type (str): Expected token type."""
    settings = get_settings()
    parts = token.split('.')
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail='Invalid token.')
    expected_signature = hmac.new(settings.auth_secret_key.encode('utf-8'), parts[0].encode('utf-8'), hashlib.sha256).digest()
    actual_signature = b64_decode(parts[1])
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise HTTPException(status_code=401, detail='Invalid token.')
    payload = json.loads(b64_decode(parts[0]).decode('utf-8'))
    if payload.get('type') != token_type:
        raise HTTPException(status_code=401, detail='Invalid token type.')
    expires_at = datetime.fromtimestamp(float(payload['exp']), tz=UTC)
    if expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail='Token expired.')
    return payload


def project_access(session: Session, user_id: int) -> list[ProjectAccess]:
    """Get user project access.
    Args:
        session (Session): Database session.
        user_id (int): User identifier."""
    rows = session.execute(
        text(
            """
            SELECT projects.project_id, projects.project_name, projects.project_slug, members.role
            FROM project_members AS members
            JOIN projects ON projects.project_id = members.project_id
            WHERE members.user_id = :user_id
              AND members.status = 'active'
              AND projects.status = 'active'
            ORDER BY projects.project_name
            """,
        ),
        {'user_id': user_id},
    )
    projects = [ProjectAccess(**dict(row._mapping)) for row in rows]
    return projects


def user_info(session: Session, user: dict[str, object]) -> UserInfo:
    """Build user information.
    Args:
        session (Session): Database session.
        user (dict[str, object]): User row."""
    data = dict(user)
    data['projects'] = project_access(session, int(data['user_id']))
    info = UserInfo(**data)
    return info


def find_user(session: Session, email: str) -> dict[str, object] | None:
    """Find user by email.
    Args:
        session (Session): Database session.
        email (str): User email."""
    row = session.execute(
        text('SELECT * FROM users WHERE lower(email) = lower(:email)'),
        {'email': email.strip()},
    ).first()
    user = dict(row._mapping) if row else None
    return user


def get_user(session: Session, user_id: int) -> dict[str, object] | None:
    """Get user by id.
    Args:
        session (Session): Database session.
        user_id (int): User identifier."""
    row = session.execute(text('SELECT * FROM users WHERE user_id = :user_id'), {'user_id': user_id}).first()
    user = dict(row._mapping) if row else None
    return user


def issue_tokens(session: Session, user_id: int) -> tuple[str, str]:
    """Issue auth tokens.
    Args:
        session (Session): Database session.
        user_id (int): User identifier."""
    settings = get_settings()
    now = datetime.now(UTC)
    access_token = sign_payload(
        {
            'sub': user_id,
            'type': 'access',
            'exp': (now + timedelta(minutes=settings.access_token_minutes)).timestamp(),
        },
    )
    refresh_token = sign_payload(
        {
            'sub': user_id,
            'type': 'refresh',
            'nonce': secrets.token_urlsafe(18),
            'exp': (now + timedelta(days=settings.refresh_token_days)).timestamp(),
        },
    )
    session.execute(
        text(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (:user_id, :token_hash, :expires_at)
            """,
        ),
        {
            'user_id': user_id,
            'token_hash': hash_token(refresh_token),
            'expires_at': now + timedelta(days=settings.refresh_token_days),
        },
    )
    session.commit()
    return access_token, refresh_token


def register_user(session: Session, request: RegisterRequest) -> TokenResponse:
    """Register user.
    Args:
        session (Session): Database session.
        request (RegisterRequest): Register request."""
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail='Password must contain at least 8 characters.')
    if find_user(session, request.email) is not None:
        raise HTTPException(status_code=409, detail='User already exists.')
    user_count = int(session.execute(text('SELECT COUNT(*) FROM users')).scalar_one())
    result = session.execute(
        text(
            """
            INSERT INTO users (email, password_hash, full_name, is_superadmin)
            VALUES (:email, :password_hash, :full_name, :is_superadmin)
            RETURNING *
            """,
        ),
        {
            'email': request.email.strip().lower(),
            'password_hash': hash_password(request.password),
            'full_name': request.full_name,
            'is_superadmin': user_count == 0,
        },
    )
    user = dict(result.first()._mapping)
    session.commit()
    access_token, refresh_token = issue_tokens(session, int(user['user_id']))
    response = TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user_info(session, user))
    return response


def login_user(session: Session, request: LoginRequest) -> TokenResponse:
    """Login user.
    Args:
        session (Session): Database session.
        request (LoginRequest): Login request."""
    user = find_user(session, request.email)
    if user is None or not verify_password(request.password, str(user['password_hash'])):
        raise HTTPException(status_code=401, detail='Invalid email or password.')
    if user['status'] != 'active':
        raise HTTPException(status_code=403, detail='User is not active.')
    session.execute(text('UPDATE users SET last_login_at = now(), updated_at = now() WHERE user_id = :user_id'), user)
    session.commit()
    access_token, refresh_token = issue_tokens(session, int(user['user_id']))
    response = TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user_info(session, user))
    return response


def refresh_access(session: Session, refresh_token: str) -> TokenResponse:
    """Refresh access token.
    Args:
        session (Session): Database session.
        refresh_token (str): Refresh token."""
    payload = verify_token(refresh_token, 'refresh')
    token_hash = hash_token(refresh_token)
    row = session.execute(
        text(
            """
            SELECT *
            FROM refresh_tokens
            WHERE token_hash = :token_hash
              AND revoked_at IS NULL
              AND expires_at > now()
            """,
        ),
        {'token_hash': token_hash},
    ).first()
    if row is None:
        raise HTTPException(status_code=401, detail='Refresh token is not active.')
    user = get_user(session, int(payload['sub']))
    if user is None or user['status'] != 'active':
        raise HTTPException(status_code=401, detail='User is not active.')
    settings = get_settings()
    now = datetime.now(UTC)
    access_token = sign_payload(
        {
            'sub': int(user['user_id']),
            'type': 'access',
            'exp': (now + timedelta(minutes=settings.access_token_minutes)).timestamp(),
        },
    )
    response = TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user_info(session, user))
    return response


def logout_user(session: Session, refresh_token: str) -> dict[str, str]:
    """Logout user.
    Args:
        session (Session): Database session.
        refresh_token (str): Refresh token."""
    session.execute(
        text(
            """
            UPDATE refresh_tokens
            SET revoked_at = now()
            WHERE token_hash = :token_hash AND revoked_at IS NULL
            """,
        ),
        {'token_hash': hash_token(refresh_token)},
    )
    session.commit()
    return {'status': 'logged_out'}
