# k8s-lab

A learning project: an app built as small containerized services, run on Kubernetes. Sean's first
hands-on microservices and Kubernetes work. The app is a monitor for his own sites (Phase 1),
growing into a morning digest (Phase 2). Runs on a local **kind** cluster on the `jupiter` VM.
Nothing here deploys anywhere.

> ⚠️ **This file is the always-loaded core and is kept small.** Detail lives in `docs/` and is
> *not* loaded automatically. **Read the relevant file before acting.** The left column is the
> action you are about to take, not a topic.
>
> | Before you… | Read |
> |---|---|
> | start a session: reconcile against `git log` / `gh issue list` | [`docs/status.md`](docs/status.md) |
> | plan the next step, or a service's shape | [`docs/plan.md`](docs/plan.md) |
> | change a manifest, a Dockerfile or a service | [`docs/gotchas.md`](docs/gotchas.md) |
> | run anything against the cluster | the Non-negotiables below |
> | want the reasoning behind a workflow rule | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Environment

- The `jupiter` VM: Ubuntu, **arm64**, 8 cores, about 7 GB RAM (about 4 GB free), Docker 29.
  Every binary and image must have an arm64 build.
- **kind** (Kubernetes in Docker) is the cluster: each Kubernetes node is a Docker container.
  Not k3s in LXD (no `/dev/kvm`), and never the droplet: it is small and runs production apps.
- Everything here is meant to cost nothing. Real money is Sean's call, named up front.

## Non-negotiables

1. **`kubectl` only ever talks to the `kind-k8s-lab` context.** Check
   `kubectl config current-context` before anything that changes the cluster. Breaking things is
   the point here, so the one thing that must never happen is breaking the wrong thing.
2. **No secret value is ever committed** (the repo is public). A Kubernetes Secret is created from
   the command line or from a gitignored file, and the manifest in git names it without holding it.
3. **Every container declares memory requests and limits.** The VM has about 4 GB to spare, and
   one runaway pod would starve Docker, VS Code and the other projects' dev stacks.
4. **Images are pinned.** Our own by an explicit version tag, never `:latest` (with kind, `:latest`
   makes Kubernetes try to pull from a registry instead of using the image loaded into the
   cluster). Third-party images by tag **and** digest.
5. **Breaking things on purpose starts with a prediction.** An Experiment issue says what you
   expect before you do it; the result goes in the issue and the notes, right or wrong.
6. **Ask before installing tools** on the VM. The issue says what and which version; Sean says go.

## Working with Sean here

- **Explain each new concept the first time it comes up**, briefly (Pods, Deployments, Services,
  kubectl, Ingress, CronJobs, Secrets…), in the chat and again in the reference notes. He is
  starting from zero with Kubernetes, so a term used before it's explained is a bug.
- When he's stuck, plain numbered steps first.
- Show the command, then what it printed, then what that means.

## Git & development workflow

Rationale lives in `CONTRIBUTING.md`; this section is the rule.

**Issue → branch → PR → squash-merge.** Do not work directly on `main` (it is protected).

1. **Every change starts from an issue**: Feature (Given/When/Then criteria), Experiment
   (prediction first) or Bug. Assign the open milestone.
2. **Branch** off `main` as `<issue#>-short-slug`.
3. **Check it for real** with the `verify` skill against the running cluster, not by reading YAML.
4. **Open a PR** with `Closes #<issue>`. Every `Scenario:` gets a `Verified by hand:` line in the
   PR body until there are tests to claim them.
5. **Squash-merge on Sean's word.** "Keep going" means do the next thing, not merge.

**Milestones are plan steps** (`docs/plan.md`), one open at a time, closed when the step is done.
**Batch by coherence, never by calendar.** Commit subjects imperative and capitalised; the body
says why.

**CI** (`.github/workflows/ci.yml`) runs ruff, pytest, a Kubernetes v1.37 schema check of `k8s/`
and each image build on every PR; wait for green before asking to merge. Dependabot opens weekly
update PRs. No CHANGELOG or versions: nothing is released.

▶️ `/wrap` runs the end-of-session sequence (`.claude/commands/wrap.md`). `.claude/README.md`
describes the rest of the harness.

## Current status

See `docs/status.md`. Step 1 is done (2026-11-07): kind v0.33.0, kubectl v1.37.2, the
`k8s-lab` cluster on Kubernetes v1.37.0 from `kind.yaml` (#2). Step 2's milestone is open with
#5 `status`, #6 `prober`, #7 CI, criteria written but not yet agreed by Sean. **Next:** his go on
#5's criteria and on #6's www question, then build #5, then #7, then #6.

## Maintainer notes (local only)

Where the notes live, the vault and memory paths and machine-specific state are in the gitignored
`CLAUDE.local.md`.
