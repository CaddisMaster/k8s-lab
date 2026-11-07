# k8s-lab

A learning project: an app built as small containerized services, run on Kubernetes. Sean's
first hands-on microservices and Kubernetes work. The plan is [`docs/plan.md`](docs/plan.md):
read it before doing anything.

## Where it came from

Sean wrote a note on his phone on 2026-11-07, the claude.ai doc
[Explore: containerized microservices](https://claude.ai/artifact/BgaUCbCz8mfaTQvGR9Dxu5)
(why, the monolith vs microservices trade-off, his questions). In an Orbit Ops session the same
day he decided:

- **Kubernetes from the start**, not Docker Compose first.
- **A separate repo**, not part of Orbit Ops or Budget Buddy. Those are production apps with
  strict workflows; this is where things get broken on purpose.
- **The app:** a monitor for his own sites (Phase 1), growing into a morning digest (Phase 2).
  He chose it over a textbook shop because he'd actually use it.

Orbit Ops (the DevOps learning app in `../orbit-ops`) has a planned Kubernetes track with a
"Cluster labs: kind & k3s" unit. What Sean learns here can feed that later; nothing here is
part of Orbit Ops's code.

## Environment

- Runs on the `jupiter` VM: Ubuntu, **arm64**, 8 cores, about 7 GB RAM (about 4 free), Docker 29.
- **kind** (Kubernetes in Docker) is the cluster. Not k3s in LXD: no `/dev/kvm`, and LXD runs
  heat up Sean's Mac. Not the droplet, ever: it's small and runs his production apps.
- Real money is Sean's call, named up front. Everything here is meant to cost nothing.
- Sean edits in VS Code over Remote-SSH; `../Jupiter.code-workspace` includes this repo.

## Working with Sean here

- **Explain each new concept the first time it comes up**, briefly (Pods, Deployments,
  Services, kubectl, Ingress, CronJobs, Secrets…). This is how he learns it.
- When he's stuck, plain numbered steps first.
- Keep `docs/log.md` as a running log: date, what was tried, what happened, what was learned.
- Lightweight on purpose: no issue/PR ceremony, no CI gates, no releases (for now). Commit to
  `main` with clear messages. **Ask before installing tools, pushing, or creating the GitHub repo.**

## State (2026-11-07)

- One commit: README and `docs/plan.md`. No GitHub remote yet (public or private is Sean's call).
- Nothing installed: `kind` and `kubectl` are not on the VM yet.
- **Next:** Phase 1, step 1: install `kind` and `kubectl` (arm64 builds, pinned versions) on
  Sean's go, create a cluster, `kubectl get nodes`.
- Open questions are at the end of `docs/plan.md`.
