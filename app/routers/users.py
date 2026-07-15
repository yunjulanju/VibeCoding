from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    current_user.is_deleted = True
    current_user.deleted_at = datetime.now(timezone.utc)
    db.add(current_user)
    db.commit()
