# `.claude/`: the harness half

`CLAUDE.md` says what the agreement is; this directory makes some of it execute. If anything here
disagrees with `CLAUDE.md` or `CONTRIBUTING.md`, this directory is what needs fixing.

```
.claude/
  agents/gotcha-auditor.md  # check a branch diff against docs/gotchas.md and the Non-negotiables (read-only)
  skills/verify/            # look at what the cluster is actually doing; refuses any context but kind-k8s-lab
  skills/beginner-audit/    # /beginner-audit <doc or note>: every term used before it's explained (read-only)
  commands/wrap.md          # /wrap: the end-of-session sequence
  settings.json             # permission allowlist: read-only kubectl, kind, git and gh
```

## The allowlist is read-only on purpose

`kubectl get`, `describe`, `logs` and friends run without a prompt. `apply`, `delete`, `scale`,
`kind create` and `kind delete` always ask. In a lab where breaking things is the point, the
prompt is the moment to check you're about to break the thing you meant to.

## ⚠️ This repo is public: mind the line

| Committed `settings.json` | Gitignored `settings.local.json` |
|---|---|
| Repo-relative commands, read-only `kubectl`/`git`/`gh` | Absolute `$HOME` paths |
| Anything true for any clone | Vault paths, anything about other machines |

## Not here yet

- **A CHANGELOG Stop hook** and a **release-prep agent**: there is no CHANGELOG and there are no
  releases. They come with CI, if they come at all.
- **Test-first and sweeper agents**: there's no code to test or sweep. Add them with the first
  service.
