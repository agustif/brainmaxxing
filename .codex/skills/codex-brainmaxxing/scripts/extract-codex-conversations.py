#!/usr/bin/env python3
"""Extract user and assistant messages from Codex session JSONL files.

Usage:
  extract-codex-conversations.py <sessions-root> <output-dir> [options]

Options:
  --batches N        Number of batch manifests to create (default: 5)
  --workspace PATH   Keep only sessions whose cwd is this path or subpath
  --from YYYY-MM-DD  Include sessions modified on or after this date
  --to YYYY-MM-DD    Include sessions modified on or before this date
  --min-size BYTES   Minimum file size in bytes (default: 500)

Output:
  <output-dir>/000_<session>.txt
  <output-dir>/batches/batch_0.txt ... batch_N.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def normalize_path(value: str) -> str:
    return str(Path(value).expanduser().resolve())


def file_mod_date(path: Path) -> date:
    return datetime.fromtimestamp(path.stat().st_mtime).date()


def extract_text_entries(content: object) -> Iterable[str]:
    if isinstance(content, str):
        yield content
        return

    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            kind = item.get("type")
            text = item.get("text")
            if kind in {"input_text", "output_text", "text"} and isinstance(text, str):
                yield text


def extract_messages(path: Path) -> list[str]:
    messages: list[str] = []

    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            if row.get("type") != "response_item":
                continue

            payload = row.get("payload")
            if not isinstance(payload, dict):
                continue
            if payload.get("type") != "message":
                continue

            role = payload.get("role")
            if role not in {"user", "assistant"}:
                continue

            for raw in extract_text_entries(payload.get("content")):
                text = raw.strip()
                if len(text) <= 10:
                    continue

                # Remove common scaffolding noise.
                if text.startswith("<environment_context>"):
                    continue
                if text.startswith("# AGENTS.md instructions"):
                    continue

                if role == "user":
                    messages.append(f"[USER]: {text[:3000]}")
                else:
                    messages.append(f"[ASSISTANT]: {text[:1200]}")

    return messages


def read_session_cwd(path: Path) -> Optional[str]:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            if row.get("type") != "session_meta":
                continue

            payload = row.get("payload")
            if not isinstance(payload, dict):
                return None

            cwd = payload.get("cwd")
            return str(cwd) if isinstance(cwd, str) else None

    return None


def cwd_matches(session_cwd: Optional[str], workspace: Optional[str]) -> bool:
    if workspace is None:
        return True
    if not session_cwd:
        return False

    try:
        session_norm = normalize_path(session_cwd)
        workspace_norm = normalize_path(workspace)
    except OSError:
        return False

    if session_norm == workspace_norm:
        return True

    prefix = workspace_norm.rstrip(os.sep) + os.sep
    return session_norm.startswith(prefix)


def list_session_files(
    root: Path,
    min_size: int,
    from_date: Optional[date],
    to_date: Optional[date],
    workspace: Optional[str],
) -> list[Path]:
    files: list[Path] = []

    for candidate in root.rglob("*.jsonl"):
        try:
            size = candidate.stat().st_size
        except OSError:
            continue

        if size < min_size:
            continue

        modified = file_mod_date(candidate)
        if from_date and modified < from_date:
            continue
        if to_date and modified > to_date:
            continue

        if not cwd_matches(read_session_cwd(candidate), workspace):
            continue

        files.append(candidate)

    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def write_batches(extracted: list[Path], output_dir: Path, batches: int) -> None:
    batches_dir = output_dir / "batches"
    batches_dir.mkdir(parents=True, exist_ok=True)

    if not extracted:
        return

    batch_size = max(1, (len(extracted) + batches - 1) // batches)

    for batch_idx in range(batches):
        start = batch_idx * batch_size
        end = (batch_idx + 1) * batch_size
        batch_files = extracted[start:end]
        if not batch_files:
            continue

        manifest = batches_dir / f"batch_{batch_idx}.txt"
        with manifest.open("w", encoding="utf-8") as handle:
            for path in batch_files:
                handle.write(str(path) + "\n")

        print(f"Batch {batch_idx}: {len(batch_files)} conversations", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract messages from Codex session JSONL files."
    )
    parser.add_argument("sessions_root", help="Root directory containing Codex session JSONL files")
    parser.add_argument("output_dir", help="Directory for extracted conversation text files")
    parser.add_argument("--batches", type=int, default=5, help="Number of batch manifests")
    parser.add_argument("--workspace", help="Filter sessions by workspace root path")
    parser.add_argument("--from", dest="from_date", type=parse_date, help="Include from date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", type=parse_date, help="Include to date (YYYY-MM-DD)")
    parser.add_argument("--min-size", type=int, default=500, help="Minimum JSONL size in bytes")

    args = parser.parse_args()

    sessions_root = Path(args.sessions_root).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    files = list_session_files(
        root=sessions_root,
        min_size=args.min_size,
        from_date=args.from_date,
        to_date=args.to_date,
        workspace=args.workspace,
    )

    date_desc = ""
    if args.from_date and args.to_date:
        date_desc = f" (from {args.from_date} to {args.to_date})"
    elif args.from_date:
        date_desc = f" (from {args.from_date})"
    elif args.to_date:
        date_desc = f" (to {args.to_date})"

    print(f"Found {len(files)} sessions{date_desc}", file=sys.stderr)

    extracted: list[Path] = []
    for idx, source in enumerate(files):
        session_id = source.stem
        out_path = output_dir / f"{idx:03d}_{session_id}.txt"
        messages = extract_messages(source)
        if not messages:
            continue

        with out_path.open("w", encoding="utf-8") as handle:
            handle.write("\n\n".join(messages))

        extracted.append(out_path)

    print(f"Extracted {len(extracted)} conversations with content", file=sys.stderr)

    write_batches(extracted, output_dir, max(1, args.batches))

    print(str(output_dir))


if __name__ == "__main__":
    main()
