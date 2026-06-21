#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_ROOT="$REPO_ROOT/skills"
TARGET_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$TARGET_ROOT"

link_skill() {
  local skill_dir="$1"
  local skill_name
  local target
  local current

  skill_name="$(basename "$skill_dir")"
  target="$TARGET_ROOT/$skill_name"

  if [ -L "$target" ]; then
    current="$(readlink "$target")"
    if [ "$current" = "$skill_dir" ]; then
      echo "linked already: $skill_name"
      return 0
    fi

    rm "$target"
    ln -s "$skill_dir" "$target"
    echo "updated: $skill_name"
    return 0
  fi

  if [ -e "$target" ]; then
    echo "skipped: $skill_name (existing non-symlink target)"
    return 0
  fi

  ln -s "$skill_dir" "$target"
  echo "linked: $skill_name"
}

for skill_dir in "$SOURCE_ROOT"/*; do
  [ -d "$skill_dir" ] || continue
  [ -f "$skill_dir/SKILL.md" ] || continue
  link_skill "$skill_dir"
done
