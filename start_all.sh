#!/bin/bash

echo "🚀 주식 분석 시스템 서버 시작 중..."

# 현재 디렉토리를 프로젝트 루트로 설정
cd "$(dirname "$0")"

# 가상환경 활성화
echo "📦 가상환경 활성화 중..."
source venv/bin/activate

# 백엔드 서버 시작 (백그라운드)
echo "🔧 백엔드 서버 시작 중..."
python -m backend.app &
BACKEND_PID=$!

# 백엔드 서버가 시작될 때까지 잠시 대기
sleep 3

# 프론트엔드 서버 시작 (백그라운드)
echo "🎨 프론트엔드 서버 시작 중..."
cd frontend
npm run serve &
FRONTEND_PID=$!

# 프로세스 ID 저장
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

echo "✅ 서버들이 시작되었습니다!"
echo "📊 백엔드 서버: http://localhost:5001"
echo "🎨 프론트엔드 서버: http://localhost:8080"
echo ""
echo "서버를 중지하려면: ./stop_all.sh"

# 현재 실행 중인 프로세스 상태 확인
sleep 2
echo ""
echo "📋 실행 중인 서버 상태:"
lsof -i :5001 -i :8080 2>/dev/null || echo "서버가 아직 시작 중입니다..."

# 스크립트가 종료되지 않도록 대기
wait 