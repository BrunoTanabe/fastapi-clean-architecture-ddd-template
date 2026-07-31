#!/usr/bin/env bash
# PostToolUse hook: format and lint a Python file that Claude just wrote or edited.
#
# Reads the hook event JSON on stdin, extracts the touched file path, and runs ruff
# against it when the file is Python and lives under app/, test/, scripts/, or migrations/.
# Exits 0 in every case: this hook keeps the tree formatted, it does not block work.

set -uo pipefail

payload="$(cat)"

# tool_input.file_path is set by Write, Edit, and NotebookEdit.
file_path="$(printf '%s' "$payload" | python3 -c '
import json
import sys

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = event.get("tool_input") or {}
print(tool_input.get("file_path") or "")
' 2>/dev/null)"

[ -n "$file_path" ] || exit 0
[ -f "$file_path" ] || exit 0

case "$file_path" in
    *.py) ;;
    *) exit 0 ;;
esac

case "$file_path" in
    */app/*|app/*|*/test/*|test/*|*/scripts/*|scripts/*|*/migrations/*|migrations/*) ;;
    *) exit 0 ;;
esac

command -v uv >/dev/null 2>&1 || exit 0

project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$project_dir" || exit 0

uv run ruff format "$file_path" >/dev/null 2>&1
uv run ruff check --fix "$file_path" 2>&1 | tail -n 20

exit 0
