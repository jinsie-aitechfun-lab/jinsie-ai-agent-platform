#!/usr/bin/env bash
set -e

# -----------------------------------------------------------------------------
# Load environment variables from .env into current shell.
#
# Usage:
#   source scripts/load_env.sh
#
# Notes:
# - Must be sourced, not executed, otherwise variables won't persist.
# - This script is a fallback for users without direnv.
# -----------------------------------------------------------------------------

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "[load_env] ERROR: .env file not found in project root."
  echo "[load_env] Please create one based on .env.example."
  return 1 2>/dev/null || exit 1
fi

echo "[load_env] Loading environment variables from $ENV_FILE ..."

# Automatically export all variables defined during sourcing
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# Basic sanity checks (fail fast)
missing=0
for key in OPENAI_API_KEY OPENAI_MODEL; do
  if [ -z "$(printenv "$key")" ]; then
    echo "[load_env] ERROR: required variable $key is not set."
    missing=1
  fi
done

if [ "$missing" -eq 1 ]; then
  echo "[load_env] Environment not fully loaded. Aborting."
  return 1 2>/dev/null || exit 1
fi

echo "[load_env] Environment loaded successfully."
