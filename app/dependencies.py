from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_token

_bearer_scheme = HTTPBearer(auto_error=False)

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="유효하지 않은 인증 정보입니다.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise _credentials_exception

    user_id = decode_token(credentials.credentials)
    if user_id is None:
        raise _credentials_exception

    user = db.execute(
        select(User).where(User.id == user_id, User.is_deleted.is_(False))
    ).scalar_one_or_none()
    if user is None:
        raise _credentials_exception

    return user
