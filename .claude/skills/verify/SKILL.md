---
name: verify
description: Look at what the k8s-lab kind cluster is actually doing (nodes, pods, rollouts, events, and what a Service really answers, from outside and from inside the cluster) to confirm a change works, not just that kubectl accepted it. Refuses to run against any context but kind-k8s-lab.
---

# Verify against the running cluster

`kubectl apply` succeeding only means the API server **accepted** the manifest. It says nothing
about whether the pod pulled its image, started, passed its probes, or answers on its Service.
This skill checks each of those, in order, and reports what it saw.

## 0. The right cluster, or stop

```bash
kubectl config current-context        # must print exactly: kind-k8s-lab
```

Anything else: **stop and report.** Do not switch contexts yourself; say which one is active and
ask. Every command below is read-only, but the habit is the point.

## 1. The cluster itself

```bash
kubectl get nodes -o wide             # STATUS must be Ready
docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}' | grep k8s-lab   # the node's memory on the VM
```

## 2. What's running

```bash
kubectl get deployments,pods,services -o wide
kubectl get events --sort-by=.lastTimestamp | tail -20
```

For each pod, the `STATUS` column means:

| STATUS | Meaning | Look at |
|---|---|---|
| `Running`, READY `1/1` | started and passing its readiness probe | step 3 |
| `Running`, READY `0/1` | started, readiness probe failing | `kubectl describe pod`, the probe and Events |
| `Pending` | not scheduled yet: usually no room (memory requests) | `kubectl describe pod`, Events |
| `ImagePullBackOff` / `ErrImagePull` | couldn't get the image. With kind: was it `kind load`ed, and is the tag not `:latest`? | Events |
| `CrashLoopBackOff` | starts, exits, is restarted, repeatedly | `kubectl logs <pod> --previous` |
| `OOMKilled` (or `Last State` in `describe`) | went over its memory limit | the limit, and what the app does at startup |

For a Deployment just changed: `kubectl rollout status deployment/<name> --timeout=60s`.

## 3. What a Service actually answers

**From outside the cluster** (the VM's shell), through a port-forward. It runs in the
background and must be stopped afterwards:

```bash
kubectl port-forward service/<name> 18080:<service-port> >/dev/null 2>&1 &
PF=$!; sleep 2
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:18080/healthz
kill $PF
```

**From inside the cluster**, which is how services find each other: by the Service's name,
through the cluster's DNS. Use one of our own pods (they have Python), so no extra image is pulled:

```bash
kubectl exec deploy/<caller> -- python -c \
  "import urllib.request as u; r=u.urlopen('http://<service>/healthz', timeout=5); print(r.status, r.read()[:200])"
```

If the outside check passes and the inside one fails, the problem is the Service's name, port or
selector, not the app.

## 4. Report

State what you ran, the exact status values, codes and the lines of output that matter, not
"it works". Name anything left running (a port-forward you couldn't kill, a pod you created).
