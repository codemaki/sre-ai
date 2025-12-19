FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 프로젝트 파일 복사
COPY pyproject.toml ./
COPY app.py ai_agent.py ./

# 의존성 설치
RUN uv pip install --system -r pyproject.toml

# 앱 실행
CMD ["python", "app.py"]
