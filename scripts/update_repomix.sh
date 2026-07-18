#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repomix_version="1.16.1"
npm_cache="${TMPDIR:-/tmp}/se-ai-command-pack-npm-cache"

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx is required to refresh docs/repomix-map.md" >&2
  exit 1
fi

cd "$repo_root"
mkdir -p "$npm_cache"
export NPM_CONFIG_CACHE="$npm_cache"
exec npx --yes "repomix@${repomix_version}" --config repomix.config.json
