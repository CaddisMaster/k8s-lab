# Gotchas

Each entry is something that already went wrong once, here, with the issue it went wrong in.
Add to it when something surprises you. Things that are only *expected* to go wrong belong in the
Non-negotiables in `CLAUDE.md` or in an Experiment issue, not here.

## kubectl

- **`kubectl exec` discards stdin unless you pass `-i`** (2026-11-11, #5). A heredoc piped into
  `kubectl exec deploy/status -- python -` printed nothing and exited 0: Python read an empty
  stdin. It needs `kubectl exec -i`. Each readiness probe also fails once at container start
  (`connection refused`, before uvicorn listens); one `Unhealthy` event per start is normal, not
  a bug.

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

- **`kubectl rollout status` says "successfully rolled out" a moment before the Service routes
  to the new pod** (2026-11-11, #5). Right after a pod was deleted and replaced, a request to
  `http://status/` from inside the cluster got `Connection refused`, and the same request a
  second later worked. The pod was `1/1 Ready`; the Service's endpoints and kube-proxy's rules
  catch up asynchronously, in well under a second. A script that checks a Service straight after
  a rollout should retry once or twice.

## Images

## Services and networking
