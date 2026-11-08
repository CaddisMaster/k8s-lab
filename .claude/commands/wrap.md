---
description: "Run the end-of-session wrap-up: PR, check the cluster, notes in one pass, merge on Sean's word."
---

Run the session wrap-up for this repo.

`CLAUDE.md` §"Git & development workflow" is the source of truth for *policy*. This command
carries the **sequence** and the **traps**. If the two disagree, `CLAUDE.md` wins and this file is
what needs fixing.

⚠️ **This repo is public.** Nothing personal belongs in this file. Vault paths and machine state
live in the gitignored `CLAUDE.local.md`. Read that for step 3; do not restate it here.

Work through the steps in order, reporting after each. Stop and ask rather than skipping: the
ordering is the point.

## 1. Open a PR for the session's work

Do not work directly on `main`.

- Every `Scenario:` of each issue being closed has a `Verified by hand:` line in the PR body:
  what was run and what it printed. Until there are tests, these lines are the only record that
  the criteria were checked.
- Open the PR with `Closes #<issue>`, one line per issue closed.
- Add this session's entry to the top of `docs/status.md`'s *Sessions*, update its *Tools* table
  if anything was installed or upgraded, and update `CLAUDE.md`'s *Current status*. Keep three
  sessions in `status.md`: move any older one, unchanged, to the top of `docs/status-archive.md`.
- A surprise that cost time goes in `docs/gotchas.md`, with its issue number.
- **Batch by coherence, never by calendar.**

## 2. Look at the cluster

If the cluster exists, run the `verify` skill for what this session changed, and say what is
still running. A kind cluster uses memory on the VM whether or not anyone is looking at it:
report its node container's figure from `docker stats --no-stream`, and ask Sean whether to leave
it up or `kind delete cluster --name k8s-lab`. Never delete it without his answer.

If an experiment ran, check its issue has *What happened* and *What it taught* filled in.

## 3. Update the notes, in ONE pass, at the very end

This is a standing rule and it is deliberate: note-writing happens once, at the end, not
incrementally through the session.

Read `CLAUDE.local.md` for where the notes live: the reference notes, the daily diary and the
memory. **Sean is new to Kubernetes, so the reference notes are the main thing this repo
produces.** Every new idea from the session gets explained there in full: what it is, why it
exists, the commands, what their output means, and what went wrong. Use `/beginner-audit` on a
note that gained a lot.

If `CLAUDE.local.md` is not present, you are in a fresh clone and this step does not apply to
you. Say so and move on.

## 4. Get it merged, on Sean's word

Push, then ask Sean to merge. **"Keep going" is not "merge".** On his word,
`gh pr merge --squash --delete-branch`, then `git switch main && git pull --ff-only`.

Once there is CI: wait for green first, and after merging read the run on `main`
(`gh run list --branch main --limit 1`). Do not re-run a red one before reading it.

⚠️ **Do not push to a branch whose PR may already have been merged.** The commit lands on the
branch and never reaches `main`. If a branch was based on another one, **rebase** it onto `main`
after the squash-merge; a merge drags the squashed commits back in as unmerged.

Finish by telling me in three or four lines: what merged, what is still open, whether the cluster
is still running, and what the next session should pick up.
