#!/usr/bin/env bash
# OpenSSH deployment with an explicitly pinned ED25519 host key.
set -euo pipefail
umask 077
DEPLOY_SSH_DIR=$(mktemp -d)
trap 'rm -rf "$DEPLOY_SSH_DIR"' EXIT
printf '%s\n' "$SERVER_SSH_KEY" > "$DEPLOY_SSH_DIR/key"
printf '%s %s\n' "$SERVER_HOST" "$SERVER_HOST_KEY" > "$DEPLOY_SSH_DIR/known_hosts"
SSH_OPTIONS=(-i "$DEPLOY_SSH_DIR/key" -o BatchMode=yes -o StrictHostKeyChecking=yes
  -o "UserKnownHostsFile=$DEPLOY_SSH_DIR/known_hosts" -o HostKeyAlgorithms=ssh-ed25519
  -o ConnectTimeout=20)
scp "${SSH_OPTIONS[@]}" src/serve.py "$SERVER_USER@$SERVER_HOST:/home/$SERVER_USER/src/serve.py"
scp "${SSH_OPTIONS[@]}" requirements-serve.txt "$SERVER_USER@$SERVER_HOST:/home/$SERVER_USER/requirements-serve.txt"
ssh "${SSH_OPTIONS[@]}" "$SERVER_USER@$SERVER_HOST" 'bash -se' <<'REMOTE'
"$HOME/bootstrap/bin/uv" pip install --python "$HOME/.venv/bin/python" -r "$HOME/requirements-serve.txt"
sudo -n systemctl restart income-api
for attempt in $(seq 1 30); do
  if curl --fail --silent --show-error --max-time 3 http://127.0.0.1:8080/healthz; then
    echo 'Health check passed'
    exit 0
  fi
  sleep 2
 done
 echo 'Health check failed'
 exit 1
REMOTE
