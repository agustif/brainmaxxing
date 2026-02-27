#!/usr/bin/env bash
# Codex native notify-hook adapter for brainmaxxing.
# Expects argv: <project-dir> <notify-payload-json>

set -euo pipefail

project_dir="${1:-$PWD}"
payload_json="${2:-}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Only act on the expected event type when payload is present.
if [[ -n "$payload_json" ]] && command -v jq >/dev/null 2>&1; then
  event_type="$(printf '%s' "$payload_json" | jq -r '.type // empty' 2>/dev/null || true)"
  if [[ "$event_type" != "agent-turn-complete" ]]; then
    exit 0
  fi
fi

# Keep this hook non-blocking/fault-tolerant.
bash "$script_dir/auto-index-brain.sh" "$project_dir" >/dev/null 2>&1 || true
