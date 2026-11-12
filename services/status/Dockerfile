# status:0.1.0. Build on the VM and load into kind; there is no registry:
#   docker build -t status:0.1.0 services/status
#   kind load docker-image status:0.1.0 --name k8s-lab
#
# Third-party image pinned by tag AND digest (the multi-arch index digest, so it resolves to the
# arm64 build on the VM and would to amd64 elsewhere). From: docker buildx imagetools inspect.
FROM python:3.12.16-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/status.db

WORKDIR /srv

# Dependencies first, so a code change doesn't reinstall them (Docker caches each layer).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a normal user, not root. /data is where the PersistentVolumeClaim is mounted.
RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin status \
 && mkdir -p /data && chown status:status /data
USER status

EXPOSE 8000
CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
