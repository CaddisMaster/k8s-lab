# Gotchas

Each entry is something that already went wrong once, here, with the issue it went wrong in.
Add to it when something surprises you. Things that are only *expected* to go wrong belong in the
Non-negotiables in `CLAUDE.md` or in an Experiment issue, not here.

## The VM and kind

- **Deleting the cluster deletes its kubectl context** (2026-11-07, #2). With no other cluster,
  `kubectl` then has no current context, and every command fails with
  `connection to the server localhost:8080 was refused` until the cluster is recreated.
- **`kubectl run --rm` doesn't always clean up** (2026-11-07, Step 2 set-up). A throwaway
  `kubectl run nettest --rm -i …` piped into `head` left the pod behind as `Completed`: `--rm`
  deletes the pod only when kubectl sees the attach end normally, and `head` closing the pipe cut
  it short. Check `kubectl get pods` after a throwaway, and pin its image like any other
  (`busybox:1.37` was used unpinned that time).

## Manifests

## Images

## Services and networking
