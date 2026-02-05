#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Claro 로컬 개발 서버 시작 스크립트
# ============================================================

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# 색상
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Claro - 민원 AI 어시스턴트 (Dev)${NC}"
echo -e "${BLUE}========================================${NC}"

# conda 환경 확인
CONDA_ENV="${CLARO_CONDA_ENV:-claro}"
PYTHON_CMD="/opt/anaconda3/envs/${CONDA_ENV}/bin/python"

if [ ! -f "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}conda 환경 '${CONDA_ENV}' 없음. 시스템 python 사용${NC}"
    PYTHON_CMD="python3"
fi

BACKEND_PORT="${BACKEND_PORT:-8011}"
FRONTEND_PORT="${FRONTEND_PORT:-3010}"

# .env 로드
if [ -f "$ROOT_DIR/.env" ]; then
    set -a
    source "$ROOT_DIR/.env"
    set +a
    echo -e "${GREEN}[OK]${NC} .env 로드 완료"
fi

# 백엔드 시작
echo -e "\n${BLUE}[1/2] 백엔드 시작 (port $BACKEND_PORT)...${NC}"
cd "$BACKEND_DIR"
$PYTHON_CMD -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$BACKEND_PORT" \
    --reload \
    --log-level info &
BACKEND_PID=$!
echo -e "${GREEN}[OK]${NC} Backend PID: $BACKEND_PID"

# 프론트엔드 시작
echo -e "\n${BLUE}[2/2] 프론트엔드 시작 (port $FRONTEND_PORT)...${NC}"
cd "$FRONTEND_DIR"

# .env.local에 BACKEND_URL 설정
echo "BACKEND_URL=http://localhost:$BACKEND_PORT" > .env.local

npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
echo -e "${GREEN}[OK]${NC} Frontend PID: $FRONTEND_PID"

echo -e "\n${GREEN}========================================${NC}"
echo -e "  Backend:  http://localhost:$BACKEND_PORT"
echo -e "  Frontend: http://localhost:$FRONTEND_PORT"
echo -e "  API Docs: http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Ctrl+C 로 종료${NC}\n"

# 종료 시 자식 프로세스 정리
cleanup() {
    echo -e "\n${YELLOW}서버 종료 중...${NC}"
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    echo -e "${GREEN}종료 완료${NC}"
}
trap cleanup EXIT INT TERM

# 대기
wait
