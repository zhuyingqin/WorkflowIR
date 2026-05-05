#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/litwatch/run_aris_prompt.sh <prompt.md>" >&2
  exit 64
fi

prompt_file="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ ! -f "$prompt_file" ]; then
  if [ -f "$repo_root/$prompt_file" ]; then
    prompt_file="$repo_root/$prompt_file"
  else
    echo "Prompt file not found: $1" >&2
    exit 66
  fi
fi

cd "$repo_root"

exec "$repo_root/target/debug/aris" \
  --model "${ARIS_MODEL:-MiniMax-M2.7}" \
  --permission-mode "${ARIS_PERMISSION_MODE:-danger-full-access}" \
  --allowedTools "${ARIS_ALLOWED_TOOLS:-Skill,read,write,edit,glob,grep,bash}" \
  prompt "$(< "$prompt_file")"
