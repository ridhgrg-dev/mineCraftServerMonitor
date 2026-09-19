from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from control_plane.core.auth import (
    hash_password,
    hash_session_token,
    new_session_token,
    normalize_email,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
COOKIE_NAME = "platform_session"
SESSION_LIFETIME = timedelta(hours=8)


class Credentials(BaseModel):
    email: str
    password: str = Field(min_length=12, max_length=1024)
    display_name: str = Field(min_length=1, max_length=100)


class LoginCredentials(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=1024)


class CurrentUser(BaseModel):
    id: UUID
    email: str
    display_name: str


async def _create_session(request: Request, response: Response, user_id: UUID) -> None:
    token = new_session_token()
    expires_at = datetime.now(UTC) + SESSION_LIFETIME
    async with request.app.state.resources.engine.begin() as connection:
        await connection.execute(
            text(
                "INSERT INTO platform.browser_sessions "
                "(id, user_id, token_hash, expires_at) "
                "VALUES (:id, :user_id, :token_hash, :expires_at)"
            ),
            {
                "id": uuid4(),
                "user_id": user_id,
                "token_hash": hash_session_token(token),
                "expires_at": expires_at,
            },
        )
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=request.app.state.settings.environment == "production",
        samesite="lax",
        max_age=int(SESSION_LIFETIME.total_seconds()),
        path="/",
    )


@router.post("/register", response_model=CurrentUser, status_code=201, operation_id="register_user")
async def register(body: Credentials, request: Request, response: Response) -> CurrentUser:
    user = CurrentUser(
        id=uuid4(), email=normalize_email(body.email), display_name=body.display_name.strip()
    )
    async with request.app.state.resources.engine.begin() as connection:
        await connection.execute(
            text(
                "INSERT INTO platform.users "
                "(id, email_normalized, display_name, password_hash) "
                "VALUES (:id, :email, :display_name, :password_hash)"
            ),
            {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "password_hash": hash_password(body.password),
            },
        )
    await _create_session(request, response, user.id)
    return user


@router.post("/login", response_model=CurrentUser, operation_id="login")
async def login(body: LoginCredentials, request: Request, response: Response) -> CurrentUser:
    async with request.app.state.resources.engine.connect() as connection:
        row = (
            (
                await connection.execute(
                    text(
                        "SELECT id, email_normalized, display_name, password_hash "
                        "FROM platform.users "
                        "WHERE email_normalized = :email"
                    ),
                    {"email": normalize_email(body.email)},
                )
            )
            .mappings()
            .one_or_none()
        )
    if row is None or not verify_password(row["password_hash"], body.password):
        from fastapi import HTTPException

        raise HTTPException(401)
    user = CurrentUser(
        id=row["id"], email=row["email_normalized"], display_name=row["display_name"]
    )
    await _create_session(request, response, user.id)
    return user
