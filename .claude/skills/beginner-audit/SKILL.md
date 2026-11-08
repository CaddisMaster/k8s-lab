---
name: beginner-audit
description: 'Read one k8s-lab doc, issue or Obsidian reference note end to end as someone who knows nothing about Kubernetes beyond what they have already read, and report every place they would get stuck: a term used before it is explained, jargon explained by more jargon, a command whose output is never described, placeholders, silent outcomes, steps run together. Read-only. Returns a list of findings with the fix for each. Run as /beginner-audit <path, note name or #issue>.'
argument-hint: <path | note name | #issue>
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash(gh issue view:*), Bash(git show:*), Bash(git log:*)
---

# Beginner audit

You are auditing one piece of writing for a reader who is **new to Kubernetes**. They know
Linux, Docker and Docker Compose, Git, Python and web apps. They don't know any Kubernetes term
until something they've read has explained it.

Your question at every line: **would this reader, having read only what comes before this line
(and the notes listed as read before it), know what this means and what to do?** If the honest
answer is "they'd have to guess, search the web or already know", that's a finding.

Difficulty is fine. A finding is never "this is hard". It's "the thing you need to understand
this isn't on the page, or isn't where you'd look for it".

## Arguments

`$ARGUMENTS` is one of:

- **A path** in this repo (`docs/plan.md`, `CONTRIBUTING.md`) or an absolute path to a note.
- **A note name** (`Services`). The notes live outside this repo; the gitignored
  `CLAUDE.local.md` says where. Find the note under that project's `reference/` folder.
- **`#N`**: a GitHub issue. Read it with `gh issue view N --comments`.

## Procedure

1. **Work out what the reader has already read.** For a reference note, the notes folder has a
   start-here note with a reading order: everything before the target counts as read. For a repo
   doc or an issue, count `CLAUDE.md`'s *Environment* section and nothing else.
2. **Build the known-terms list** from what's been read: each term, command, flag, field and
   abbreviation, and where it was first **explained**. Explained means a sentence or a table row
   says what it is or does. Appearing in a code block, a YAML comment or a link doesn't count.
3. **Read the target top to bottom, in order.** Prose, tables, code blocks, YAML and its
   comments, command output.
4. **Write down each finding at the line it happens**, with the question the reader would ask
   right there.

## What to look for

### 1. Used before it's explained
- A Kubernetes term (`Pod`, `ReplicaSet`, `Service`, `selector`, `namespace`, `context`,
  `control plane`, `kubelet`, `CNI`), a `kubectl` subcommand or flag, or a YAML field used before
  any sentence says what it is.
- **Jargon explained by more jargon**: "a Service selects Pods by label" when neither *selects*
  nor *label* has been explained.
- An idea borrowed from a later note, with no pointer to it.
- Acronyms never expanded (`CRI`, `CNI`, `RBAC`, `CRD`).

### 2. Output nobody explains
- A command shown without what it prints, or its output shown without saying which columns
  matter and what the values mean (`READY 0/1`, `RESTARTS 4`, `AGE`).
- A status the reader will meet (`Pending`, `CrashLoopBackOff`, `ImagePullBackOff`) named but not
  explained.

### 3. YAML without a map
- A manifest where a field that matters isn't explained in the prose: `apiVersion`, `kind`,
  `metadata.labels`, `spec.selector`, `template`, `containerPort` vs `targetPort` vs `port`.
- Two fields that must match (a selector and a label, a Service's `targetPort` and the
  container's port) without the page saying they must.

### 4. Placeholders
`foo`, `my-app`, `<name>` where a real name from this project (`prober`, `status`, `k8s-lab`)
would do. A beginner can't run a placeholder, and can't tell which part is syntax and which is a
name you chose.

### 5. Named, not explained
- A list or table of labels with no sentence saying what each is *for*.
- An arrow or shorthand (`Deployment → ReplicaSet → Pod`) never spelled out in words.
- "Simply", "just" or "obviously" in front of a step that isn't.

### 6. Silent outcomes and surprises
- A command that prints nothing, or only `created`/`configured`, where the reader would expect
  to see something happen. Say how to check it worked.
- Behaviour a beginner wouldn't expect, unwarned: a deleted pod coming back, `kubectl apply`
  succeeding for a pod that never starts, a change taking effect seconds later.
- Something that differs between kind and a "real" cluster, with no note saying so
  (`LoadBalancer` staying `<pending>`, images needing `kind load`).

### 7. Steps run together
- Several actions in one sentence where numbered steps would read better.
- An unclear "it", "this" or "that one".
- No way to tell when a step is finished.

## Output

Return **only** the findings, plain English, short sentences:

````markdown
<One or two sentences: who reads this and where they'd get stuck.>

1. **<The finding, as a short claim.>** <Where it is (heading, line, code block), quoted briefly.
   What the reader asks at that point. Where the term is first explained, if anywhere.>
   **Fix:** <the sentence to add, the real name to use, the output to show.>
2. …
N. **Smaller:** <minor findings, one line each.>

**Checked and clear:** <what you looked at that was fine.>
````

Most serious first: something needed to follow a step that isn't there, then terms used before
they're explained, then the rest. If the writing is clean, say so in one line and list what you
checked. Never invent findings to fill the list. Two real findings is a good result.

## Constraints

- **Read-only.** Never edit a file, commit, or comment on the issue yourself. The caller applies
  the fixes.
- You aren't fact-checking Kubernetes. If you notice something that looks wrong, add it as one
  line under **Smaller** and say it needs checking.
- Don't review style or tone, only whether a beginner can follow it.
