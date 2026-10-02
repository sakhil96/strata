# Strata: the static front end and its API in one image for Snowpark Container Services.

FROM node:22-bookworm-slim@sha256:43ac6c60b8f89723f746e8a92ce91abd5017e627ce1ddfe4238355d3a30b772c AS web
WORKDIR /src/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
COPY ontology/generated/glossary.json /src/ontology/generated/glossary.json
ENV NEXT_TELEMETRY_DISABLED=1
RUN npx next build

FROM python:3.11-slim-bookworm@sha256:2333bd330d12de02514770b3585cad313644316047cdee24a7acfdece6de6efb AS app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 SCM_BACKEND=snowflake SCM_WEB_OUT=/app/web/out
WORKDIR /app
COPY requirements.lock ./
RUN pip install --require-hashes --no-deps -r requirements.lock && useradd --uid 10001 --no-create-home strata
COPY api/ api/
COPY ontology/semantic.py ontology/resolver.py ontology/metrics.yaml ontology/
COPY ontology/generated/glossary.json ontology/generated/glossary.json
COPY eval/report.json eval/governance_snapshot.json eval/
COPY --from=web /src/web/out web/out
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/live', timeout=2)"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--no-server-header"]
