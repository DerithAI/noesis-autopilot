# EVO-HUB Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install deps
COPY ventures/evo-hub/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ventures/evo-hub/backend/ ./backend/
COPY ventures/evo-hub/agents/ ./agents/
COPY ventures/evo-hub/memory/ ./memory/
COPY noesis_autopilot.py ./
COPY noesis_insights.py ./
COPY venture-swarm.py ./
COPY forge-bot/ ./forge-bot/

# Create dirs for ventures
RUN mkdir -p /app/ventures

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
