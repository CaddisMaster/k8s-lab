Closes #

## Why
<!-- A sentence or two. The diff shows what; explain why. -->

## How it was verified
<!-- What did you actually run, and what did it print? "kubectl apply worked" is not enough:
     apply accepts a manifest whose pod never starts. -->
- [ ] `kubectl config current-context` was `kind-k8s-lab`
- [ ] Checked in the running cluster (the `verify` skill, or `kubectl get` / `describe` / `logs`)
- [ ] Every `Scenario:` in the issue has a line below

<!-- One line per scenario until there are tests to claim them:
Verified by hand: #<n> "<Scenario title>" — what you ran and what it printed
-->

## For an experiment
<!-- Delete if this isn't one. -->
- **Predicted:**
- **Happened:**
- **Why the difference:**

## Checklist
- [ ] Every container has memory requests and limits
- [ ] Images pinned (ours by version tag, third-party by tag and digest), with arm64 builds
- [ ] No secret values, tokens or kubeconfig in the diff
- [ ] New ideas are explained in the session notes
