FROM python:3.11-slim AS base
WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY api/ api/
COPY ontology/generated/ ontology/generated/
COPY eval/ eval/

FROM node:22-slim AS web-build
WORKDIR /web
COPY web/package.json web/tsconfig.json web/next.config.ts web/tailwind.config.ts ./
RUN npm install
COPY web/ .
RUN npm run build

FROM base AS final
COPY --from=web-build /web/out /app/web/out

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
