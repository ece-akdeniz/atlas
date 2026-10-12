FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORTAL_DB=/data/portal.sqlite3
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock && useradd --uid 10001 --create-home atlas && mkdir /data && chown atlas:atlas /data
COPY portal ./portal
COPY scripts ./scripts
USER atlas
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "60", "portal.app:app"]
