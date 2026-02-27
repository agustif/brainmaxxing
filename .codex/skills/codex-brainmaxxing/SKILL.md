---
name: codex-brainmaxxing
description: Persistent memory workflow for Codex using a markdown brain vault in `brain/`. Use when you need to preserve durable project knowledge, run end-of-session reflection, audit stale or redundant memory notes, mine past Codex sessions for recurring patterns, or emulate Claude-style memory hooks in Codex.
---

# Codex Brainmaxxing

Maintain a durable `brain/` vault that improves future Codex sessions.

Use four operations: `brain`, `reflect`, `meditate`, and `ruminate`.

## Quick Start

1. Read `brain/index.md` before non-trivial work.
2. After notable learning or correction, run the `reflect` workflow.
3. Periodically run `meditate` to prune stale notes and tighten principles.
4. Occasionally run `ruminate` to mine historical Codex sessions.

## Hook Emulation In Codex

Codex has no first-class `SessionStart`/`PostToolUse` hook API like Claude.

Emulate the same behavior with scripts:

```bash
# Session-start equivalent
bash .codex/skills/codex-brainmaxxing/scripts/inject-brain.sh "$PWD"

# Post-brain-edit equivalent
bash .codex/skills/codex-brainmaxxing/scripts/auto-index-brain.sh "$PWD"
```

Use these scripts in shell wrappers, CI steps, or your personal session bootstrap.

## Operation: brain

Treat `brain/` as high-signal durable memory.

Rules:
- Keep one topic per file.
- Keep file names lowercase and hyphenated.
- Keep index files link-only with `[[wikilinks]]`.
- Keep each note short and actionable.
- Ensure every brain note is reachable from `brain/index.md`.

Before writing:
- Read `brain/index.md` first.
- Read related note files before adding a new one.
- Prefer editing an existing note over creating a near-duplicate.

After writing:
- Update `brain/index.md` links if files were added or removed.
- Run `auto-index-brain.sh` to detect and fix index drift.

Durability gate:
- Write to `brain/` only if it helps future unrelated tasks.
- If it only matters for the current task, keep it in local task docs.

## Operation: reflect

Run at session end or after user corrections.

Workflow:
1. Read `brain/index.md`.
2. Scan the current session for:
- mistakes and corrections
- repeated user preferences
- codebase gotchas and decisions
- friction in tooling or workflow
3. Drop trivial, one-off, or already-captured items.
4. Route each learning:
- `brain/` for durable knowledge
- skill files for skill behavior changes
- backlog/todo for follow-up work
5. Update indexes.

Structural enforcement check:
- If a learning can become a script, lint, metadata rule, or runtime check, encode that instead of writing prose.

Reflection summary format:

```markdown
## Reflect Summary
- Brain: [files created/updated]
- Skills: [skill files modified]
- Structural: [scripts/rules/checks added]
- Todos: [follow-up items]
```

## Operation: meditate

Audit and evolve memory quality.

### 1. Build snapshots

```bash
bash .codex/skills/codex-brainmaxxing/scripts/snapshot.sh brain/ /tmp/brain-snapshot.md
bash .codex/skills/codex-brainmaxxing/scripts/snapshot.sh .codex/skills/ /tmp/skills-snapshot.md
```

### 2. Spawn auditor

Create one sub-agent for audit using `references/agents.md`.

Inputs:
- `/tmp/brain-snapshot.md`
- project root path
- optional `AGENTS.md` path

### 3. Early-exit gate

If fewer than 3 actionable findings, skip reviewer and apply fixes directly.

### 4. Spawn reviewer

Create one sub-agent for synthesis/distillation/skill review.

Inputs:
- `/tmp/brain-snapshot.md`
- `/tmp/skills-snapshot.md`
- auditor report
- `brain/principles.md`

### 5. Apply changes

Apply high-confidence fixes directly:
- prune stale or duplicate notes
- condense verbose notes
- add missing wikilinks
- resolve principle tensions
- update skill guidance when findings are skill-specific

### 6. Housekeep

Update `brain/index.md` for added/removed files.

Meditation summary format:

```markdown
## Meditate Summary
- Pruned: [deleted/condensed/merged]
- Extracted: [new principles with evidence counts]
- Skill review: [findings and applied changes]
- Housekeep: [index updates]
```

## Operation: ruminate

Mine past Codex sessions for uncaptured patterns.

### 1. Snapshot brain

```bash
bash .codex/skills/codex-brainmaxxing/scripts/snapshot.sh brain/ /tmp/brain-snapshot-ruminate.md
```

### 2. Extract project session logs

```bash
python3 .codex/skills/codex-brainmaxxing/scripts/extract-codex-conversations.py \
  "$HOME/.codex/sessions" \
  /tmp/codex-ruminate \
  --workspace "$PWD" \
  --batches 5
```

### 3. Spawn batch analyzers

Spawn one sub-agent per batch manifest (`/tmp/codex-ruminate/batches/batch_N.txt`).

Each agent extracts:
- user corrections
- recurring preferences
- technical learnings
- workflow patterns
- repeated frustrations
- skill gaps

### 4. Synthesize with strict filtering

Keep only findings with frequency or impact.

Discard one-offs unless they reveal factual drift in existing brain notes.

### 5. Apply approved changes

- Update existing brain notes first.
- Create new notes only when needed.
- Route skill-specific findings to skill files.
- Update `brain/index.md` after changes.

### 6. Cleanup

```bash
rm -rf /tmp/codex-ruminate
```

## Resources

- `scripts/snapshot.sh`: Concatenate markdown trees into a snapshot file.
- `scripts/inject-brain.sh`: Session-start brain index injection.
- `scripts/auto-index-brain.sh`: Rebuild `brain/index.md` on drift.
- `scripts/extract-codex-conversations.py`: Parse Codex session JSONL into analyzable batches.
- `references/agents.md`: Prompt specs and report templates for auditor/reviewer agents.
