from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.models import User
from app.utils.auth import authenticate_user, blacklist_token, get_current_user
from app.utils.jwt import jwt

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    Local login endpoint for users with password authentication
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last_login timestamp
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    payload = {
        "uid": user.id,
        "email": user.email,
        "name": user.name,
        "is_admin": user.is_admin,
        "exp": int(
            datetime.now(timezone.utc).timestamp()
            + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Logout endpoint that blacklists the current token and updates logout time
    """
    # Update user's last logout time
    result = await db.execute(
        select(User).where(User.id == current_user.user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if user:
        user.last_logout = datetime.now(timezone.utc)
        await db.commit()

    # Blacklist the token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        blacklist_token(token)
    return {"message": "Successfully logged out"}
