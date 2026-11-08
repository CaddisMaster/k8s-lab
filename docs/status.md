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
- **No CI, CHANGELOG or versions until the first service** (2026-11-07). They arrive in its issue.
- **Notes are written in detail.** Sean is new to Kubernetes, so each concept is explained the
  first time it appears, in the session and in the reference notes.

## Tools

| Tool | Version | Installed | Checked |
|---|---|---|---|
| kind | v0.33.0 (go1.26.7, linux/arm64) | 2026-11-07, `~/.local/bin/kind` (#2) | `kind-linux-arm64.sha256sum` from the release: `20022bee…3867a2` OK |
| kubectl | v1.37.2 (linux/arm64) | 2026-11-07, `~/.local/bin/kubectl` (#2) | `kubectl.sha256` from dl.k8s.io: `fcc16f63…a03509` OK |
| Cluster | Kubernetes v1.37.0, `kindest/node` pinned by digest in `kind.yaml` | 2026-11-07 (#2) | kind v0.33.0's default node image; kubectl is the same minor |

Upgrading: change kind, the node image in `kind.yaml` (from kind's release notes) and kubectl
together, keeping kubectl within one minor version of the cluster, then rebuild the cluster.

## Sessions

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
- **Next:** #2. Install kind and kubectl on Sean's go.
