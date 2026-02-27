# Brainmaxxing

![brainmaxxing](brainmaxxing.png)

Stupid simple persistent memory for Claude Code. A markdown vault that your agent reads at session start and writes to when it learns something. It's also an [Obsidian](https://obsidian.md) vault, so you can browse your agent's memory yourself.

Comes with 16 engineering principles as starter content and four skills that form a learning loop: `reflect` after sessions, `ruminate` over past conversations, `meditate` to audit and prune. Two hooks handle the plumbing: injecting the brain index at startup and rebuilding it when files change.

```mermaid
graph LR
    A[talk to claude] --> B["/reflect"]
    B --> C["brain/"]
    C --> D["/meditate"]
    D --> E[your skills get better]
    D --> F[your principles evolve]
    F --> C
    F --> E
    G["/ruminate"] --> C
    G -. mines .-> H[conversation history]
```

## Usage

**`/reflect`**: Run this at the end of a session, or after Claude makes a mistake and you correct it. It scans the conversation for things worth remembering and writes them to the brain. Most of your brain content will come from this.

**`/meditate`**: Run this after your brain has accumulated some content. It reviews your skills against what's in the brain, finds contradictions, and suggests improvements to them. Also prunes stale notes and surfaces unstated principles hiding across multiple entries.

**`/ruminate`**: Run this occasionally (weekly, monthly, whenever). It digs through your past Claude Code conversations looking for patterns that `/reflect` missed. Corrections you gave, preferences you repeated, knowledge that never got captured. Good for bootstrapping a brain from an existing conversation history.

You don't need to use all three. `/reflect` alone gets you most of the value.

## Installation

Tell Claude Code:

> Install brainmaxxing from https://github.com/poteto/brainmaxxing into this project.

It needs to:

1. Copy `brain/` into the project root (the starter vault)
2. Copy `.agents/skills/` (brain, reflect, ruminate, meditate)
3. Copy `.claude/hooks/` and merge hook config into `.claude/settings.json`
4. Append the brain instructions from `CLAUDE.md` into the project's `CLAUDE.md`

## Codex-Native Add-on

This fork adds a Codex-native skill at:

`/.codex/skills/codex-brainmaxxing`

It ports the same `brain` / `reflect` / `meditate` / `ruminate` loop for Codex and includes:

1. `scripts/extract-codex-conversations.py` for mining `~/.codex/sessions/**/*.jsonl`
2. `scripts/inject-brain.sh` and `scripts/auto-index-brain.sh` to emulate startup and post-edit memory hooks
3. `references/agents.md` with Codex sub-agent prompt/report templates

Quick run:

```bash
bash .codex/skills/codex-brainmaxxing/scripts/inject-brain.sh "$PWD"
python3 .codex/skills/codex-brainmaxxing/scripts/extract-codex-conversations.py "$HOME/.codex/sessions" /tmp/codex-ruminate --workspace "$PWD" --batches 5
```

## License

MIT
