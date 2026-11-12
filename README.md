# k8s-lab

A learning project: an app built as small containerized services, run on Kubernetes (a local
[kind](https://kind.sigs.k8s.io/) cluster on the `jupiter` VM).

The app is a monitor for my own sites, which grows into a morning digest. See
[`docs/plan.md`](docs/plan.md).

Separate from Orbit Ops and Budget Buddy on purpose: this is where things get broken to see
what happens.

## How work happens here

Every change starts as a GitHub issue (Feature, Experiment or Bug), goes on a branch, and lands
as a squash-merged pull request. Each step of the plan is a milestone. See
[`CONTRIBUTING.md`](CONTRIBUTING.md); where things stand is in [`docs/status.md`](docs/status.md).

## What's in the repo

```
kind.yaml           the cluster (kind create cluster --config kind.yaml)
k8s/                manifests: namespace.yaml first, then one file per service
services/<name>/    each service: app/, tests/, Dockerfile, pinned requirements
docs/               plan, status, gotchas
```

## Running a service

Each service is built on the VM and loaded straight into kind; there is no registry.

```bash
python3 -m venv .venv && .venv/bin/pip install -r services/status/requirements-dev.txt
(cd services/status && ruff check . && ../../.venv/bin/python -m pytest)
docker build -t status:0.1.0 services/status
kind load docker-image status:0.1.0 --name k8s-lab
kubectl apply -f k8s/namespace.yaml && kubectl apply -f k8s/status.yaml
kubectl -n k8s-lab rollout status deployment/status
kubectl -n k8s-lab port-forward service/status 18080:80   # then http://localhost:18080/
```
