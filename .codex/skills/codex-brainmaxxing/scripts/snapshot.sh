#!/bin/sh
# Concatenate all markdown files in a directory tree into one snapshot file.
# Usage: snapshot.sh <directory> <output-file>

set -eu

dir="${1:?Usage: snapshot.sh <directory> <output-file>}"
output="${2:?Usage: snapshot.sh <directory> <output-file>}"

: > "$output"

find "$dir" -name '*.md' -type f -not -path '*/node_modules/*' | sort | while IFS= read -r file; do
  printf '=== %s ===\n' "$file" >> "$output"
  cat "$file" >> "$output"
  printf '\n\n' >> "$output"
done

echo "$output"
