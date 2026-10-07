#!/usr/bin/env bash
# Execute as root on the newly created Ubuntu VM.
set -euo pipefail
DEPLOY_USER=azureuser
DEPLOY_HOME=/home/azureuser
export DEBIAN_FRONTEND=noninteractive
# cloud-init write_files can create the home directory before Azure creates the user.
chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME" "$DEPLOY_HOME/requirements-serve.txt"
apt-get update -qq
apt-get install -y -qq python3-venv curl
if [ ! -f /swapfile ]; then
  fallocate -l 1G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  printf '/swapfile none swap sw 0 0\n' >> /etc/fstab
fi
sudo -u "$DEPLOY_USER" python3 -m venv "$DEPLOY_HOME/bootstrap"
sudo -u "$DEPLOY_USER" "$DEPLOY_HOME/bootstrap/bin/pip" install 'uv==0.12.19'
sudo -u "$DEPLOY_USER" env HOME="$DEPLOY_HOME" \
  "$DEPLOY_HOME/bootstrap/bin/uv" venv --python 3.11 "$DEPLOY_HOME/.venv"
sudo -u "$DEPLOY_USER" env HOME="$DEPLOY_HOME" UV_LINK_MODE=copy \
  "$DEPLOY_HOME/bootstrap/bin/uv" pip install --python "$DEPLOY_HOME/.venv/bin/python" \
  -r "$DEPLOY_HOME/requirements-serve.txt"
install -d -o "$DEPLOY_USER" -g "$DEPLOY_USER" "$DEPLOY_HOME/models" "$DEPLOY_HOME/src"
cat > /etc/systemd/system/income-api.service <<'EOF'
[Unit]
Description=Adult income inference API
Wants=network-online.target
After=network-online.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser
EnvironmentFile=/home/azureuser/.env
Environment=OMP_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
ExecStart=/home/azureuser/.venv/bin/python /home/azureuser/src/serve.py
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable income-api
printf 'VM bootstrap completed; API starts after Azure environment and model are available.\n'
