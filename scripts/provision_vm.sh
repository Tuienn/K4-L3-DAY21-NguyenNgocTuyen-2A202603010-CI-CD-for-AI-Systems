#!/usr/bin/env bash
# Creates exactly one small VM for serving; training stays off this VM.
set -euo pipefail
LAB_GROUP=rg-income-lab
LAB_LOCATION=southeastasia
LAB_VM=income-api
LAB_VM_SIZE=Standard_B2ats_v2
mkdir -p .secrets
chmod 700 .secrets
if [ ! -f .secrets/income_deploy ]; then
  ssh-keygen -q -t ed25519 -f .secrets/income_deploy -N '' -C income-lab-deploy
fi
az group create --name "$LAB_GROUP" --location "$LAB_LOCATION" \
  --tags purpose=income-ci-cd-lab owner=Tuienn --output none
if az vm show --resource-group "$LAB_GROUP" --name "$LAB_VM" --output none 2>/dev/null; then
  az vm show --resource-group "$LAB_GROUP" --name "$LAB_VM" --show-details \
    --query '{name:name,size:hardwareProfile.vmSize,publicIp:publicIps,location:location}' -o json
  exit 0
fi
az vm create --resource-group "$LAB_GROUP" --name "$LAB_VM" \
  --location "$LAB_LOCATION" --size "$LAB_VM_SIZE" \
  --image Canonical:ubuntu-24_04-lts:server:24.04.202609040 \
  --security-type TrustedLaunch --enable-vtpm true --enable-secure-boot true --admin-username azureuser --authentication-type ssh \
  --ssh-key-values .secrets/income_deploy.pub \
  --storage-sku Standard_LRS --os-disk-size-gb 30 \
  --public-ip-sku Standard --nsg-rule SSH \
  --custom-data scripts/cloud-init.yaml \
  --tags purpose=income-ci-cd-lab owner=Tuienn \
  --query '{id:id,publicIp:publicIpAddress,powerState:powerState,location:location}' -o json
