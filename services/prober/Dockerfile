# prober:0.1.0. Build on the VM and load into kind; there is no registry:
#   docker build -t prober:0.1.0 services/prober
#   kind load docker-image prober:0.1.0 --name k8s-lab
#
# Third-party image pinned by tag AND digest (the multi-arch index digest, so it resolves to the
# arm64 build on the VM and would to amd64 elsewhere). From: docker buildx imagetools inspect.
FROM python:3.12.15-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/prober.db

WORKDIR /srv

# Dependencies first, so a code change doesn't reinstall them (Docker caches each layer).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a normal user, not root. /data is where the PersistentVolumeClaim is mounted.
RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin prober \
 && mkdir -p /data && chown prober:prober /data
USER prober

EXPOSE 8000
CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
