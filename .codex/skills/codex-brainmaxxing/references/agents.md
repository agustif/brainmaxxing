# Agent Prompt Specs (Codex)

Spawn agents with `spawn_agent` and gather outputs with `wait`.

Agents should be read-only analysts that return markdown reports.

## Common Prompt Inclusions

Include all items below in each agent prompt:
- Brain snapshot path (`/tmp/brain-snapshot.md` or variant).
- Brain vault root (`brain/`).
- Project root path.
- Optional `AGENTS.md` path when present.
- Rule: use Grep/Glob only for codebase verification, not for re-reading full snapshot content.
- Requirement: return structured markdown only.

## Auditor

Inputs:
- brain snapshot
- project root
- optional `AGENTS.md`

Tasks:
- Parse snapshot using `=== path ===` separators.
- Build wikilink graph and detect orphans.
- Cross-check notes against current codebase reality.
- Flag notes as:
- outdated
- redundant
- low-value
- verbose
- orphaned
- Audit `AGENTS.md` for stale or contradictory instructions.
- Provide suggested action per finding (update, merge, condense, delete).

Early-exit rule:
- If actionable findings are fewer than 3, recommend skipping reviewer.

## Reviewer

Inputs:
- brain snapshot
- skills snapshot
- auditor report
- `brain/principles.md`

Sections:

### 1. Synthesis
- propose missing `[[wikilinks]]`
- identify principle tensions
- suggest boundary clarifications

### 2. Distillation
- infer missing principles from repeated evidence
- require each new principle to be:
- independent
- evidenced by at least 2 notes
- actionable

### 3. Skill Review
- check skill/process contradictions against principles
- identify structural enforcement opportunities
- detect duplicated prose that should become mechanisms
- suggest concise frontmatter trigger improvements

## Report Template

Use this format:

```markdown
## Audit Results — Brain
- X notes flagged (outdated/redundant/low-value/verbose/orphaned)
- [one line per finding]

## Audit Results — AGENTS.md
- X sections flagged (outdated/redundant/verbose/contradictory)
- [one line per finding]

## Synthesis Results
- M connections proposed
- T tensions identified
- [one line per item]

## Distiller Results
- P principles proposed
- [one line + evidence count]

## Skill Review Results
- S skills reviewed, N findings
- [one line per finding]
```
