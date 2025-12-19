#!/bin/bash

# Jenkins AI Agent 실행 스크립트

set -e

echo "========================================"
echo "  Jenkins AI Agent"
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

# uv 설치 확인
if ! command -v uv &> /dev/null; then
    echo "📦 uv가 설치되어 있지 않습니다. 설치 중..."
    echo ""
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
    echo "✅ uv 설치 완료!"
    echo "   쉘을 재시작하거나 다음 명령을 실행하세요:"
    echo "   source ~/.bashrc (또는 ~/.zshrc)"
    echo ""
    exit 0
fi

# 의존성 설치
echo "📦 의존성 설치 중..."
uv pip install -e .
echo ""

# Agent 실행
echo "🚀 Agent 시작..."
echo ""
python -m src.main
