#!/usr/bin/env bash

if [ -z "$BASH_VERSION" ]; then
  echo "Error: this script must be run with Bash." >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository." >&2
  exit 1
fi

SERVICE_URL="https://codespotter.vercel.app/analyze"
MAX_SIZE=$((500 * 1024))   # 500 KB

echo -n "codespotter is reviewing your commit... "

payload="[]"
while read -r status path; do
  [[ "$status" == "D" || -z "$path" ]] && continue

  base_blob="HEAD^:$path"

  size_base=$(git cat-file -s "$base_blob" 2>/dev/null || echo 0)
  (( size_base > MAX_SIZE )) && continue

  content_base=$(git show "$base_blob" 2>/dev/null | jq -Rs .)
  raw_patch=$(git diff --unified=3 HEAD^ HEAD -- "$path")
  content_patch=$(jq -Rs . <<< "$raw_patch")

  payload=$(jq \
    --arg p "$path" \
    --arg base "$content_base" \
    --arg patch "$content_patch" \
    '. += [{path: $p, base: $base, patch: $patch}]' <<< "$payload")
done < <(git diff-tree --no-commit-id --name-status -r HEAD)

# Send payload to backend
if ! resp=$(printf '%s' "$payload" | curl -sS --fail -H "Content-Type: application/json" --data-binary @- "$SERVICE_URL"); then
  echo "Failed."
  exit 1
fi

if [[ "$resp" == "NOTHING_TO_REPORT" ]]; then
  echo "Nothing to report."
  exit 0
fi

html=$(jq -r .html <<< "$resp")
if [[ -z "$html" || "$html" == "null" ]]; then
  echo "Failed."
  exit 1
fi

tmp=$(mktemp "${TMPDIR:-/tmp}/codespotter_XXXXXX")
mv "$tmp" "$tmp.html"
tmp="$tmp.html"
printf '%s' "$html" > "$tmp"

echo
if command -v xdg-open >/dev/null; then
  xdg-open "$tmp"
elif command -v open >/dev/null; then
  open "$tmp"
else
  echo "Result: $tmp"
fi
