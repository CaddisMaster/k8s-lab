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
