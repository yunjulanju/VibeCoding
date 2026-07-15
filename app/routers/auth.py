from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: SignupRequest,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    existing = db.execute(
        select(User).where(
            or_(User.email == payload.email, User.username == payload.username)
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일 또는 아이디입니다.",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user = db.execute(
        select(User).where(User.email == payload.email, User.is_deleted.is_(False))
    ).scalar_one_or_none()

    # 계정 존재 여부를 노출하지 않도록 실패 시 동일한 응답을 반환한다.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    return TokenResponse(access_token=create_access_token(user.id))
