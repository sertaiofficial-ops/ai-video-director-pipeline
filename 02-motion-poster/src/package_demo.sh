#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 OUTPUT_ZIP FILE [FILE ...]" >&2
  exit 2
fi

OUTPUT_ZIP="$(realpath -m "$1")"
shift
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

for FILE in "$@"; do
  if [[ ! -f "$FILE" ]]; then
    echo "Missing file: $FILE" >&2
    exit 1
  fi
  cp -L "$FILE" "$WORK_DIR/"
done

mkdir -p "$(dirname "$OUTPUT_ZIP")"
rm -f "$OUTPUT_ZIP"
(
  cd "$WORK_DIR"
  zip -q "$OUTPUT_ZIP" ./*
)
unzip -t "$OUTPUT_ZIP" >/dev/null
printf 'Archive verified: %s\n' "$OUTPUT_ZIP"
