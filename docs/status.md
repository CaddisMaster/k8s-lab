# Status

Standing decisions and the last three sessions, newest first. Older sessions are in
[`status-archive.md`](status-archive.md), moved there unchanged by `/wrap`, so this file stays
short enough to read at the start of a session.

## Standing decisions

- **Kubernetes from the start**, not Docker Compose first. Compose is already familiar; the point
  is to learn what Kubernetes adds.
- **kind on the `jupiter` VM** is the cluster. It costs nothing, and a broken cluster is one
  `kind delete cluster` away from a fresh one. Not k3s in LXD (no `/dev/kvm`), never the droplet.
- **A repo of its own**, public, separate from every production app. This is where things get
  broken on purpose.
- **The app is one Sean will use:** a monitor for his own sites (Phase 1), then a morning digest
  (Phase 2). `docs/plan.md` has both.
- **The workflow is issue → branch → PR → squash-merge**, with Given/When/Then criteria, and
  Experiment issues that write the prediction down first. Milestones are plan steps, one open at
  a time. Merges happen on Sean's word.
- **CI since the first service** (2026-11-11, #7): ruff, pytest, kubeconform and image builds on
  every PR, all five checks required on `main`. No CHANGELOG or versions: nothing is released.
- **Dependabot bumps are reviewed, not rubber-stamped** (2026-11-11): a major or minor Python
  base-image bump is ignored by config; patch bumps and tool bumps come as weekly PRs.
- **Notes are written in detail.** Sean is new to Kubernetes, so each concept is explained the
  first time it appears, in the session and in the reference notes.

## Tools

| Tool | Version | Installed | Checked |
|---|---|---|---|
| kind | v0.33.0 (go1.26.7, linux/arm64) | 2026-11-07, `~/.local/bin/kind` (#2) | `kind-linux-arm64.sha256sum` from the release: `20022bee…3867a2` OK |
| kubectl | v1.37.2 (linux/arm64) | 2026-11-07, `~/.local/bin/kubectl` (#2) | `kubectl.sha256` from dl.k8s.io: `fcc16f63…a03509` OK |
| Cluster | Kubernetes v1.37.0, `kindest/node` pinned by digest in `kind.yaml` | 2026-11-07 (#2) | kind v0.33.0's default node image; kubectl is the same minor |
| kubeconform | v0.8.0, run as `ghcr.io/yannh/kubeconform` by digest, in CI and by hand | 2026-11-11 (#7), not installed | image digest in `.github/workflows/ci.yml` |
| Python tooling | system `python3` 3.12.3 and `ruff` 0.16.4 (already on the VM); a repo `.venv` (gitignored) from `requirements-dev.txt` | 2026-11-11 (#5) | each service pins its own `ruff` and `pytest` exactly |

Upgrading: change kind, the node image in `kind.yaml` (from kind's release notes) and kubectl
together, keeping kubectl within one minor version of the cluster, then rebuild the cluster.

## Sessions

### 2026-11-11: Step 2 done: `status` (#5), CI (#7), `prober` (#6)

- **#8 merged** (the previous session's record), then three PRs in the issue order agreed that
  morning: **#5 → #9**, **#7 → #10**, **#6 → #13**, each squash-merged on Sean's word with every
  scenario verified by hand in the cluster. Step 2's milestone closed; **Step 3: break it on
  purpose** opened, with no issues yet.
- **`status`** (`services/status`, `k8s/status.yaml`): FastAPI over SQLite, image `status:0.1.0`
  built on the VM and `kind load`ed; namespace `k8s-lab`, a Deployment (`replicas: 1`,
  `Recreate`), a Service `status` on port 80 → 8000, a 1 Gi PVC on kind's `standard` class,
  readiness `/readyz` (checks the database), liveness `/healthz` (process only), 64Mi/128Mi, runs
  as uid 1000. 12 tests. Deleting its pod: replaced in ~2 s, the 12 recorded checks still there.
- **CI** (`.github/workflows/ci.yml`, `dependabot.yml`): per service `ruff check`, `ruff format
  --check`, `pytest`; `kubeconform -strict -kubernetes-version 1.37.0` over `k8s/`; `docker build`
  of each Dockerfile. Every job runs on every PR so each can be required; Actions pinned by SHA.
  First run green in 16 s. Dependabot opened two PRs within minutes: **#12** (ruff 0.16.4 → 0.17.4
  for `status`) merged; **#11** (python 3.12.15 → 3.15.0) closed, and `dependabot.yml` now ignores
  major and minor Python bumps.
- **`prober`** (`services/prober`, `k8s/prober.yaml`): a ConfigMap `prober-config` (`SITES` as
  `name=url` pairs, `STATUS_URL=http://status`, interval 60 s, timeout 10 s) via `envFrom`, a PVC,
  a Deployment, **no Service** (nothing calls it). 15 tests. Checked by hand: two rounds of three
  sites in 87 s; results on status's page within the minute; a `dead=http://127.0.0.1:9/` site
  added through the ConfigMap and a `rollout restart` was recorded `DOWN … ConnectError` while the
  others carried on; with status scaled to 0 prober logged `could not send`, kept the results as
  `sent=False`, 0 restarts. The decision on www: prober checks its home page.
- **Memory:** status ~38 MiB, prober ~42 MiB, the node container 545 → 752 MiB with both running.
  The VM kept ~3.6 GB available.
- **Gotchas added** (#5): `kubectl exec` needs `-i` for stdin; a Service can refuse connections for
  a moment after `rollout status` reports success; one `Unhealthy` readiness event per container
  start is normal.
- **Left for later:** status lists any site that ever had a check, so a site removed from prober's
  list lingers as "no data". An unsent result is never re-sent (Step 3's first experiment). The
  two services' `ruff` pins differ (0.17.4 vs 0.16.4) until Dependabot's next round.
- **Left running:** the cluster with both services, unless Sean says otherwise at the wrap.
- **Next:** Step 3's Experiment issues, prediction first: delete status's pod mid-round; scale
  prober to 0 and watch the page go to "no data".

### 2026-11-07 (later): the cluster exists (#2); Step 2 set up

- **#2 merged (#4):** kind v0.33.0 and kubectl v1.37.2, arm64, SHA-256 checked, in `~/.local/bin`.
  `kind.yaml` pins `kindest/node:v1.37.0` by digest. First create took 24 s, and a rebuild 9.5 s
  with the image cached. The node is `NotReady` for its first ~10 s, then `Ready`. An empty
  cluster settles at **~536 MiB**; the VM keeps ~3.4 GB available with all dev stacks up.
- **Deleting the cluster removes its kubectl context too.** With no other cluster, `kubectl`
  then has no context at all.
- **Pods reach the internet**: a throwaway pod fetched learn's `/healthz`. learn and budget
  answer `/healthz` with 200; **www has none (404)**, its `/` is 200, so #6 checks www's `/`
  unless Sean adds a `/healthz` there.
- **Step 1 milestone closed; Step 2 opened** with #5 (`status`), #6 (`prober`), #7 (CI).
  Criteria are written, not yet agreed. Proposed order: #5, #7, #6.
- **Left running:** the `k8s-lab` cluster, unless Sean says otherwise at the wrap.
- **Next:** Sean agrees #5's criteria (and the www question on #6); then build #5.

### 2026-11-07: the repo, the workflow and the notes (#1)

- **GitHub:** `CaddisMaster/k8s-lab`, public. Squash-merge only, branches deleted on merge, `main`
  protected (PR required, linear history, no force pushes, admins included, conversations
  resolved). No required checks: there's no CI yet.
- **Labels:** `experiment`, `cluster`, `notes`, plus `triage`, `cross-repo`, `ci`,
  `dependencies`. **Milestone:** *Step 1: a cluster* (#1, #2).
- **The harness:** `/wrap`, the `verify` skill (cluster checks, refuses any context but
  `kind-k8s-lab`), `/beginner-audit` (finds terms used before they're explained, in a doc or a
  note), and the `gotcha-auditor` agent. `.claude/README.md` lists them.
- **Not brought over yet:** the CHANGELOG Stop hook and a release-prep agent (no CHANGELOG or
  releases), and a Dependabot config (nothing to update). Each comes when its subject does.
- **Notes:** the vault has a K8s Lab section with reference notes covering the Kubernetes ideas
  Phase 1 needs, before any of them are used.
