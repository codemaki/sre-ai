#!/bin/bash

# Slack 봇 배포 스크립트
# macOS (docker-compose)와 Ubuntu (docker compose) 모두 지원

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Docker Compose 명령어 감지
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo -e "${GREEN}✓ docker-compose 명령어를 사용합니다 (macOS)${NC}"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    echo -e "${GREEN}✓ docker compose 명령어를 사용합니다 (Ubuntu)${NC}"
else
    echo -e "${RED}✗ Docker Compose를 찾을 수 없습니다.${NC}"
    echo "Docker Compose를 먼저 설치해주세요."
    exit 1
fi

# .env 파일 확인
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env 파일이 없습니다.${NC}"
    if [ -f .env.example ]; then
        echo "  .env.example을 .env로 복사합니다..."
        cp .env.example .env
        echo -e "${YELLOW}  .env 파일을 편집하여 Slack 토큰을 입력하세요!${NC}"
        exit 1
    else
        echo -e "${RED}✗ .env.example 파일도 없습니다.${NC}"
        exit 1
    fi
fi

# 명령어 파싱
ACTION=${1:-deploy}

case $ACTION in
    deploy|up)
        echo -e "${GREEN}📦 배포를 시작합니다...${NC}"
        $DOCKER_COMPOSE down 2>/dev/null || true
        $DOCKER_COMPOSE build
        $DOCKER_COMPOSE up -d
        echo -e "${GREEN}✅ 배포가 완료되었습니다!${NC}"
        echo "로그를 확인하려면: $0 logs"
        ;;

    down|stop)
        echo -e "${YELLOW}🛑 컨테이너를 중지합니다...${NC}"
        $DOCKER_COMPOSE down
        echo -e "${GREEN}✅ 중지되었습니다.${NC}"
        ;;

    restart)
        echo -e "${YELLOW}🔄 재시작합니다...${NC}"
        $DOCKER_COMPOSE restart
        echo -e "${GREEN}✅ 재시작되었습니다.${NC}"
        ;;

    logs)
        echo -e "${GREEN}📋 로그를 확인합니다 (Ctrl+C로 종료)...${NC}"
        $DOCKER_COMPOSE logs -f slack-bot
        ;;

    status)
        echo -e "${GREEN}📊 컨테이너 상태:${NC}"
        $DOCKER_COMPOSE ps
        ;;

    clean)
        echo -e "${RED}🗑️  모든 컨테이너와 이미지를 제거합니다...${NC}"
        read -p "정말 삭제하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $DOCKER_COMPOSE down -v --rmi all
            echo -e "${GREEN}✅ 제거되었습니다.${NC}"
        else
            echo "취소되었습니다."
        fi
        ;;

    *)
        echo "사용법: $0 {deploy|up|down|stop|restart|logs|status|clean}"
        echo ""
        echo "명령어:"
        echo "  deploy, up  - 빌드 및 시작 (기본값)"
        echo "  down, stop  - 중지"
        echo "  restart     - 재시작"
        echo "  logs        - 로그 확인"
        echo "  status      - 상태 확인"
        echo "  clean       - 완전 제거"
        exit 1
        ;;
esac
