#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
python3 "$SCRIPT_DIR/run_banana_flow_prompt_pack.py" \
  --source-dir "${SERTAI_PROMPTS_DIR:-$REPO_ROOT/prompts}" \
  --output-dir "${SERTAI_OUTPUT_DIR:-$REPO_ROOT/output/banana_flow_automation}" \
  "$@"
