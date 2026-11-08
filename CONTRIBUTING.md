# Contributing to k8s-lab

This file gives the workflow's rules and the reasons for them; `CLAUDE.md` is the short form.
It is a learning repo, so the rules are about two things: agreeing what "done" means before
starting, and keeping a record good enough to learn from later.

## 1. Get it running

Nothing to run yet. Phase 1, step 1 (#2) installs `kind` and `kubectl` and creates the cluster;
this section gets the commands then.

## 2. The workflow

1. **Issue first.** Pick the template that fits:
   - **Feature**: something new (a service, a manifest, a tool). Acceptance criteria in
     Given/When/Then form, so "done" is agreed before anything exists.
   - **Experiment**: breaking something on purpose. You write what you expect to happen
     **before** you do it. A wrong prediction is the most useful result there is, and you only get
     it if the prediction was written down first.
   - **Bug**: something behaving differently from what you expected, found by accident.
2. **Branch** `<issue#>-short-slug` from `main`.
3. **Check it in the cluster.** A manifest that `kubectl apply` accepts can still describe a pod
   that never starts. The `verify` skill looks at what the cluster is actually doing.
4. **PR** with `Closes #N` and the template filled in honestly. Until there are tests, each
   `Scenario:` from the issue gets a line in the PR body:
   `Verified by hand: #N "<Scenario title>" — what you ran and what it printed`.
5. **Squash-merge.** One commit per issue on `main`, so `git log` reads as a list of steps.
   `main` is protected: no direct pushes, no force pushes.

### Milestones

Each step of `docs/plan.md` is a milestone. One is open at a time, and an issue that doesn't
belong to it waits. The next step's milestone is created when the current one closes.

### How much goes in one PR

Batch by **coherence**: a shared set of files, or one thing you could explain in a sentence.
Never by calendar ("everything from Tuesday").

### Commit messages

Imperative, capitalised subject ("Add the prober Deployment"); the body explains *why*.

## 3. What comes later

- **CI** (lint, tests, a schema check of the manifests) arrives in the issue that adds the first
  service. Until then there is nothing for it to check.
- **CHANGELOG and versions** arrive with CI, if they turn out to be useful. Nothing here is ever
  deployed, so a release would only be a label.

## 4. Security expectations

- The repo is public. No secrets, tokens or kubeconfig files in it. `.gitignore` covers the
  obvious ones; a Kubernetes Secret's value is never in a manifest.
- Nothing here touches the droplet or any production app.
