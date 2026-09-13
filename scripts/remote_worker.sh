#!/usr/bin/env bash
# Remote worker script to execute commands on Fedora PC (pc)
set -euo pipefail

TARGET_HOST="${1:-pc}"
shift || true
COMMAND="${*:-uv run pytest}"

echo "==> Running on ${TARGET_HOST}: ${COMMAND}"
ssh -o BatchMode=yes -o ConnectTimeout=10 "${TARGET_HOST}" "
  export PATH=\$HOME/.local/bin:\$PATH
  cd ~/Developer/cipher-lab
  ${COMMAND}
"
