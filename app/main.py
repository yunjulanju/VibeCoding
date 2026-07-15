from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, users

# 초기 스키마 생성 (단순 구성; 추후 Alembic 도입 가능)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UE5 Auth Server")

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
