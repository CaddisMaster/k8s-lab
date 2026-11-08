# The plan: a site monitor, then a morning digest

Decided 2026-11-07: Kubernetes from the start, on a local kind cluster, in a repo of its own.
The first app is a monitor for my own sites, and it grows into a morning digest.

Background (why microservices, the trade-off, the open questions) is in the claude.ai doc
[Explore: containerized microservices](https://claude.ai/artifact/BgaUCbCz8mfaTQvGR9Dxu5).

- **Where:** a kind cluster on the `jupiter` VM. It costs nothing extra and never touches the droplet.
- **Repo:** separate from Orbit Ops and Budget Buddy. Issue → branch → PR → squash-merge, with
  each step below as a milestone (`CONTRIBUTING.md`). Breaking things on purpose is an Experiment
  issue, prediction first. No CI or releases until the first service. Sessions are recorded in
  `docs/status.md`, and what I learn goes in my notes.
- **Code:** each service is a few FastAPI routes. SQLite first, then a Postgres per service once
  the basics work.

## Phase 1: site monitor

| Service    | What it does                                                                 | Owns          |
|------------|------------------------------------------------------------------------------|---------------|
| `prober`   | Every minute, checks `/healthz` on learn, budget and www; records status code and response time | check results |
| `status`   | Works out uptime and incidents, serves a page I can look at                  | incidents     |
| `notifier` | Messages me when a site goes down, once                                      | alerts sent   |

1. Create the kind cluster and check it with `kubectl get nodes` (#2).
2. Deploy `prober` and `status`, each as a Deployment with a Service. `prober` calls `status` by
   its Service name.
3. Break it on purpose. Delete `status`'s pod and see what `prober` does with its results. Scale
   `prober` to 0: `status` must show "no data", not all green.
4. Add an Ingress so the browser sees one address.
5. Add `notifier` behind a message queue. Kill `notifier` and see whether alerts are lost or only late.

## Phase 2: morning digest

Small collectors each fetch one thing. A `digest` builder runs every morning as a Kubernetes
CronJob and combines them. If a collector fails, the digest still goes out and says which part
is missing.

| Collector | What it reports                                        | Needs                              |
|-----------|--------------------------------------------------------|------------------------------------|
| uptime    | Last 24 hours from `status`                            | Phase 1                            |
| github    | Open issues and PRs across my repos                    | A read-only token, as a Kubernetes Secret |
| backups   | Whether last night's droplet dumps arrived and look complete | Access to the VM's backups folder |
| orbit-ops | Streak and today's module                              | An API Orbit Ops doesn't have yet  |

The digest is delivered through Phase 1's `notifier`.

## Later

- Tracing one request across services.
- Login across services, or a gateway.
- Helm, then the same services on k3s.

## Open questions

- How does `notifier` reach me: a push service, or email?
- The backups collector reads files on the VM, which means mounting a host folder into kind. Worth it, or leave it out?
- The orbit-ops collector needs a small API in Orbit Ops: an Orbit Ops issue of its own, later.
