FROM python:3.12-slim

ARG PRODUCT_DIR=mcp-guardrails
ARG PORT=8090

LABEL org.opencontainers.image.title="ThinkNEO MCP Product"
LABEL org.opencontainers.image.url="https://thinkneo.app"

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --no-create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup shared/ shared/
COPY --chown=appuser:appgroup ${PRODUCT_DIR}/src/ src/

USER appuser

EXPOSE ${PORT}

ENV APP_PORT=${PORT}
CMD python3 -m uvicorn src.server:app --host 0.0.0.0 --port ${APP_PORT} --workers 1
