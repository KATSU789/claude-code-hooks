#!/usr/bin/env bash
set -euo pipefail

# Check if ruff is installed
if ! python3 -m ruff --version &> /dev/null; then
  # Ruff is not installed, skip linting
  echo "Ruff is not installed. Skipping Python linting."
  echo "To install ruff, run: pip3 install ruff"
  exit 0
fi

# ruff は stdout に警告を、exit=1 で終了する
# python3を使用（多くのシステムでのデフォルト）
R="$(python3 -m ruff check . 2>&1)" || status=$? || true

if [[ "${status:-0}" -ne 0 ]]; then
  # Claude に自動修正させたいので JSON を stdout
  jq -n --arg reason "$R" '{"decision":"block","reason":$reason}'
  exit 0             # ← exit 0 で OK、decision:block が効く
fi

# 警告ゼロなら正常終了
exit 0
