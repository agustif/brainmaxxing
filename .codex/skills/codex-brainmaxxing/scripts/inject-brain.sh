#!/usr/bin/env bash
# Emulate Claude SessionStart hook for Codex.
# Prints brain/index.md when present.

set -euo pipefail

project_dir="${1:-${CODEX_PROJECT_DIR:-$PWD}}"
brain_index="$project_dir/brain/index.md"

if [ -f "$brain_index" ]; then
  echo "Brain vault index — read relevant files before acting:"
  echo
  cat "$brain_index"
fi
