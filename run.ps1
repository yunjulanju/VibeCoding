# UE5 Auth Server 실행 스크립트
# 사용법: 프로젝트 루트에서  ./run.ps1
#   (기본) 코드 변경 시 자동 재시작(--reload) 개발 모드로 실행
#   -NoReload : --reload 없이 실행 (host 0.0.0.0, 배포/외부접속용)
#   -NoDb     : docker MySQL 기동/대기 건너뛰기 (DB가 이미 떠 있을 때)
param(
    [switch]$NoDb,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# 1) 가상환경 확인 및 활성화
$activate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "[1/4] .venv 가 없어 새로 생성합니다..." -ForegroundColor Cyan
    python -m venv .venv
    & $activate
    Write-Host "      의존성 설치 중..." -ForegroundColor Cyan
    pip install -r requirements.txt
} else {
    Write-Host "[1/4] 가상환경 활성화" -ForegroundColor Cyan
    & $activate
}

# 2) .env 확인
if (-not (Test-Path (Join-Path $PSScriptRoot ".env"))) {
    Write-Host "[2/4] .env 가 없어 .env.example 로부터 생성합니다." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    $secret = python -c "import secrets; print(secrets.token_urlsafe(32))"
    (Get-Content ".env") -replace "change-me-to-a-secure-random-string", $secret | Set-Content ".env" -Encoding utf8
    Write-Host "      JWT_SECRET_KEY 를 랜덤 값으로 채웠습니다." -ForegroundColor Green
} else {
    Write-Host "[2/4] .env 확인 완료" -ForegroundColor Cyan
}

# 3) MySQL 기동 및 healthy 대기
if (-not $NoDb) {
    Write-Host "[3/4] MySQL(docker) 기동..." -ForegroundColor Cyan
    docker compose up -d

    Write-Host "      MySQL 상태 대기 중..." -ForegroundColor Cyan
    $healthy = $false
    for ($i = 0; $i -lt 30; $i++) {
        $status = docker inspect --format='{{.State.Health.Status}}' (docker compose ps -q mysql) 2>$null
        if ($status -eq "healthy") { $healthy = $true; break }
        Start-Sleep -Seconds 2
    }
    if ($healthy) {
        Write-Host "      MySQL 준비 완료" -ForegroundColor Green
    } else {
        Write-Host "      MySQL 가 아직 healthy 상태가 아닙니다. 'docker compose logs mysql' 로 확인하세요." -ForegroundColor Yellow
    }
} else {
    Write-Host "[3/4] -NoDb: MySQL 기동 건너뜀" -ForegroundColor DarkGray
}

# 4) 서버 실행
Write-Host "[4/4] 서버 시작 → http://localhost:8000  (문서: /docs)" -ForegroundColor Cyan
if ($NoReload) {
    uvicorn app.main:app --host 0.0.0.0 --port 8000
} else {
    uvicorn app.main:app --reload
}
