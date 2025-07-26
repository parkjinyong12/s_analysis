#!/bin/bash

echo "🛑 주식 분석 시스템 서버 중지 중..."

# 백엔드 서버 중지
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🔧 백엔드 서버 중지 중 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm .backend_pid
    else
        echo "🔧 백엔드 서버가 이미 중지되었습니다."
        rm .backend_pid
    fi
else
    echo "🔧 백엔드 서버 PID 파일을 찾을 수 없습니다."
fi

# 프론트엔드 서버 중지
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🎨 프론트엔드 서버 중지 중 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm .frontend_pid
    else
        echo "🎨 프론트엔드 서버가 이미 중지되었습니다."
        rm .frontend_pid
    fi
else
    echo "🎨 프론트엔드 서버 PID 파일을 찾을 수 없습니다."
fi

# 포트 사용 중인 프로세스 강제 종료
echo "🔍 포트 5001, 8080 사용 중인 프로세스 확인 중..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || echo "포트 5001 사용 중인 프로세스가 없습니다."
lsof -ti:8080 | xargs kill -9 2>/dev/null || echo "포트 8080 사용 중인 프로세스가 없습니다."

echo "✅ 모든 서버가 중지되었습니다!" 