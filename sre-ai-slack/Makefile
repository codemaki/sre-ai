.PHONY: help build up down restart logs clean

# Docker Compose 명령어 자동 감지
DOCKER_COMPOSE := $(shell which docker-compose 2>/dev/null)
ifndef DOCKER_COMPOSE
	DOCKER_COMPOSE := docker compose
endif

help: ## 사용 가능한 명령어 표시
	@echo "사용 가능한 명령어:"
	@echo "  make build    - Docker 이미지 빌드"
	@echo "  make up       - 컨테이너 시작 (백그라운드)"
	@echo "  make down     - 컨테이너 중지 및 제거"
	@echo "  make restart  - 컨테이너 재시작"
	@echo "  make logs     - 로그 확인 (실시간)"
	@echo "  make clean    - 컨테이너, 이미지, 볼륨 모두 제거"

build: ## Docker 이미지 빌드
	$(DOCKER_COMPOSE) build

up: ## 컨테이너 시작 (백그라운드)
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Slack 봇이 시작되었습니다. 'make logs'로 로그를 확인하세요."

down: ## 컨테이너 중지 및 제거
	$(DOCKER_COMPOSE) down

restart: ## 컨테이너 재시작
	$(DOCKER_COMPOSE) restart
	@echo "✅ Slack 봇이 재시작되었습니다."

logs: ## 로그 확인 (실시간)
	$(DOCKER_COMPOSE) logs -f slack-bot

clean: ## 컨테이너, 이미지, 볼륨 모두 제거
	$(DOCKER_COMPOSE) down -v --rmi all
	@echo "✅ 모든 리소스가 제거되었습니다."

deploy: ## 전체 배포 (빌드 + 시작)
	$(DOCKER_COMPOSE) down || true
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d
	@echo "✅ 배포가 완료되었습니다."
