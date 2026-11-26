FROM node:22-bookworm-slim AS frontend
WORKDIR /build/webapp
COPY webapp/package.json ./
RUN npm install --no-audit --no-fund
COPY benchmark_protocol.json /build/benchmark_protocol.json
COPY webapp/ ./
RUN npm run build
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY requirements.txt requirements-preview.txt ./
RUN pip install --no-cache-dir -r requirements-preview.txt
COPY . .
COPY --from=frontend /build/webapp/dist /app/webapp/dist
RUN python -m unittest discover -s tests -v
CMD ["sh","-c","exec python -m uvicorn preview_api:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
