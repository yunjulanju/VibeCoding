#!/usr/bin/env bash
# UE5 Auth Server 실행 스크립트 (Linux/Ubuntu)
# 사용법: 프로젝트 루트에서  ./run.sh
#   uvicorn app.main:app --host 0.0.0.0 (외부접속 허용) 으로 서버 실행
#   --no-db     : docker MySQL 기동/대기 건너뛰기 (DB가 이미 떠 있을 때)
set -euo pipefail

cd "$(dirname "$0")"

NO_DB=0
for arg in "$@"; do
    case "$arg" in
        --no-db)     NO_DB=1 ;;
        *) echo "알 수 없는 옵션: $arg"; exit 1 ;;
    esac
done

# python 실행기 결정
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python

# 1) 가상환경 확인 및 활성화
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "\033[36m[1/4] .venv 가 없어 새로 생성합니다...\033[0m"
    "$PY" -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    echo -e "\033[36m      의존성 설치 중...\033[0m"
    pip install --upgrade pip >/dev/null
    pip install -r requirements.txt
else
    echo -e "\033[36m[1/4] 가상환경 활성화\033[0m"
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

# 2) .env 확인
if [ ! -f ".env" ]; then
    echo -e "\033[36m[2/4] .env 가 없어 .env.example 로부터 생성합니다.\033[0m"
    cp .env.example .env
    SECRET=$("$PY" -c "import secrets; print(secrets.token_urlsafe(32))")
    # 구분자로 | 사용 (secret 에 / 가 포함될 수 있으므로)
    sed -i "s|change-me-to-a-secure-random-string|${SECRET}|" .env
    echo -e "\033[32m      JWT_SECRET_KEY 를 랜덤 값으로 채웠습니다.\033[0m"
else
    echo -e "\033[36m[2/4] .env 확인 완료\033[0m"
fi

# docker compose 명령 결정 (v2 plugin vs 구버전 docker-compose)
if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    DC=""
fi

# 3) MySQL 기동 및 healthy 대기
if [ "$NO_DB" -eq 0 ]; then
    if [ -z "$DC" ]; then
        echo -e "\033[33m[3/4] docker(compose) 를 찾을 수 없어 MySQL 기동을 건너뜁니다.\033[0m"
    else
        echo -e "\033[36m[3/4] MySQL(docker) 기동...\033[0m"
        $DC up -d

        echo -e "\033[36m      MySQL 상태 대기 중...\033[0m"
        HEALTHY=0
        CID=$($DC ps -q mysql)
        for _ in $(seq 1 30); do
            STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CID" 2>/dev/null || echo "")
            if [ "$STATUS" = "healthy" ]; then HEALTHY=1; break; fi
            sleep 2
        done
        if [ "$HEALTHY" -eq 1 ]; then
            echo -e "\033[32m      MySQL 준비 완료\033[0m"
        else
            echo -e "\033[33m      MySQL 가 아직 healthy 상태가 아닙니다. '$DC logs mysql' 로 확인하세요.\033[0m"
        fi
    fi
else
    echo -e "\033[90m[3/4] --no-db: MySQL 기동 건너뜀\033[0m"
fi

# 4) 서버 실행
echo -e "\033[36m[4/4] 서버 시작 → http://localhost:8000  (문서: /docs)\033[0m"
uvicorn app.main:app --host 0.0.0.0
