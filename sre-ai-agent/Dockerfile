FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose API port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Run the API server
CMD ["python", "src/main.py"]
