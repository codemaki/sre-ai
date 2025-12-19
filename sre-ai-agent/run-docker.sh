#!/bin/bash

# Jenkins AI Agent Docker 실행 스크립트

set -e

echo "========================================"
echo "  Jenkins AI Agent (Docker)"
echo "========================================"
echo ""

# .env 파일 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다."
    echo "   .env.example을 복사하여 .env 파일을 생성하고 설정을 입력하세요."
    echo ""
    echo "   cp .env.example .env"
    exit 1
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    exit 1
fi

# Docker Compose 명령어 감지 (V1: docker-compose, V2: docker compose)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✅ Docker Compose V1 감지"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "✅ Docker Compose V2 감지"
else
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    echo "   Docker Desktop을 설치하거나 다음 명령으로 설치하세요:"
    echo ""
    echo "   # Docker Compose V2 (권장)"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi
echo ""

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
$DOCKER_COMPOSE_CMD down 2>/dev/null || true
echo ""

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
$DOCKER_COMPOSE_CMD build
echo ""

# 컨테이너 실행
echo "🚀 API 서버 시작..."
echo ""
$DOCKER_COMPOSE_CMD up -d

echo ""
echo "✅ Jenkins AI Agent API 서버가 시작되었습니다!"
echo ""
echo "API 엔드포인트:"
echo "  - Health Check: http://localhost:8000/health"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - Chat API:     http://localhost:8000/api/chat"
echo "  - Stream API:   http://localhost:8000/api/chat/stream"
echo ""
echo "로그 확인: $DOCKER_COMPOSE_CMD logs -f"
echo "중지:      $DOCKER_COMPOSE_CMD down"
echo ""
