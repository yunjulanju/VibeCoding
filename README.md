# UE5 Auth Server

Unreal Engine 5 클라이언트를 위한 인증 백엔드. FastAPI + MySQL + JWT.

기능: **회원가입 · 로그인 · 내 정보 조회 · 회원탈퇴(soft delete)**

## 요구 사항
- Python 3.11+
- Docker (로컬 MySQL 실행용)

## 빠른 시작

```bash
# 1) 의존성 설치
python -m venv .venv
.venv/Scripts/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) 환경 변수 준비 (.env 는 커밋하지 않음)
cp .env.example .env
#   → JWT_SECRET_KEY 를 안전한 랜덤 값으로 교체:
#     python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3) MySQL 기동
docker compose up -d

# 4) 서버 실행
uvicorn app.main:app --reload
```

- API 서버: http://localhost:8000
- Swagger 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

## 테스트

테스트는 MySQL 없이 SQLite 로 실행됩니다.

```bash
pytest
```

## API

| 메서드 | 경로 | 인증 | 설명 |
|---|---|---|---|
| POST | `/auth/signup` | — | 회원가입 |
| POST | `/auth/login` | — | 로그인 → JWT 발급 |
| GET | `/users/me` | Bearer | 내 정보 조회 |
| DELETE | `/users/me` | Bearer | 회원탈퇴 (soft delete) |

### POST /auth/signup
```json
// 요청
{ "email": "player@example.com", "username": "player1", "password": "password123" }
// 201 응답
{ "id": 1, "email": "player@example.com", "username": "player1", "created_at": "..." }
```
- 이메일 또는 아이디 중복 시 `409`, 형식 오류 시 `422`.
- 비밀번호는 8자 이상, 아이디는 3~50자.

### POST /auth/login
```json
// 요청 (로그인은 이메일로만)
{ "email": "player@example.com", "password": "password123" }
// 200 응답
{ "access_token": "<JWT>", "token_type": "bearer" }
```
- 이메일/비밀번호 불일치 또는 탈퇴 계정은 `401` (동일 메시지).

### GET /users/me · DELETE /users/me
- 헤더에 `Authorization: Bearer <access_token>` 필요.
- `GET` → 프로필 반환. `DELETE` → `204`, 이후 해당 계정은 로그인/토큰 사용 불가.

## Unreal Engine 5 연동

UE5 는 `HttpModule` 로 JSON 을 주고받습니다.

1. **로그인** — `/auth/login` 에 이메일·비밀번호를 POST 하고 응답의 `access_token` 을 저장.
2. **인증 요청** — 이후 보호된 요청에 헤더를 첨부:
   ```
   Authorization: Bearer <access_token>
   ```

C++ 예시 (요청 헤더 설정):
```cpp
TSharedRef<IHttpRequest> Req = FHttpModule::Get().CreateRequest();
Req->SetURL(TEXT("http://localhost:8000/users/me"));
Req->SetVerb(TEXT("GET"));
Req->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *AccessToken));
Req->ProcessRequest();
```

로그인/회원가입 요청 시에는 `Content-Type: application/json` 헤더와 함께 JSON 본문을 전송하면 됩니다.

> CORS 는 브라우저 전용이라 UE5 네이티브 클라이언트에는 불필요합니다. 웹 프론트엔드를
> 추가할 경우 FastAPI 의 `CORSMiddleware` 를 설정하세요.

## 설정 (`.env`)

| 키 | 설명 |
|---|---|
| `DATABASE_URL` | MySQL 연결 문자열 |
| `JWT_SECRET_KEY` | JWT 서명 시크릿 (반드시 교체) |
| `JWT_ALGORITHM` | 기본 `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료(분), 기본 60 |

## 참고
- 초기 스키마는 앱 시작 시 자동 생성됩니다. 스키마 변경 이력 관리가 필요해지면 Alembic 도입을 고려하세요.
- 회원탈퇴는 soft delete 이며, 탈퇴한 이메일/아이디는 재사용되지 않습니다(재가입 불가).
