#!/usr/bin/env bash
# Emulate Claude PostToolUse hook for Codex.
# Rebuilds brain/index.md when the markdown file set drifts.

set -euo pipefail

project_dir="${1:-${CODEX_PROJECT_DIR:-$PWD}}"
brain_dir="$project_dir/brain"
index="$brain_dir/index.md"

[ -d "$brain_dir" ] || exit 0
[ -f "$index" ] || exit 0

# All markdown files except index.md (relative path without .md).
disk="$({
  find "$brain_dir" -name '*.md' ! -name 'index.md' -type f \
    | sed "s|^$brain_dir/||; s|\.md$||" \
    | sort
} || true)"

# Wikilinks currently in index.
indexed="$(sed -n 's/.*\[\[\([^]]*\)\]\].*/\1/p' "$index" | sort)"

[ "$disk" = "$indexed" ] && exit 0

emit_links() {
  while IFS= read -r item; do
    [ -z "$item" ] && continue
    printf -- '- [[%s]]\n' "$item"
  done
}

dirs="$(printf '%s\n' "$disk" | grep '/' | sed 's|/.*||' | sort -u || true)"

{
  echo "# Brain"

  for section in $dirs; do
    files="$(printf '%s\n' "$disk" | grep "^$section\(/\|$\)" || true)"
    [ -z "$files" ] && continue

    header="$(printf '%s' "$section" | sed 's/./\U&/')"
    printf '\n## %s\n' "$header"
    printf '%s\n' "$files" | emit_links
  done

  standalone="$(printf '%s\n' "$disk" | grep -v '/' || true)"
  if [ -n "$standalone" ]; then
    printf '\n## Other\n'
    printf '%s\n' "$standalone" | emit_links
  fi

  echo
} > "$index"
