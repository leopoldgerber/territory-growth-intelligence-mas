from pydantic import BaseModel


class ProjectAccess(BaseModel):
    project_id: int
    project_name: str
    project_slug: str
    role: str


class UserInfo(BaseModel):
    user_id: int
    email: str
    full_name: str | None = None
    status: str
    is_superadmin: bool = False
    projects: list[ProjectAccess] = []


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    user: UserInfo


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
