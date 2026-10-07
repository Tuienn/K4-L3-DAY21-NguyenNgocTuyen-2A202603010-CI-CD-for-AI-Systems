"""Prepare lab storage and local credentials. This script never writes GitHub Secrets."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContainerSasPermissions, generate_container_sas

ACCOUNT = 'stincometuyen261008'
GROUP = 'rg-income-lab'
CONTAINER = 'income-lab'


def main():
    keys = json.loads(subprocess.check_output([
        'az', 'storage', 'account', 'keys', 'list', '-g', GROUP, '-n', ACCOUNT, '-o', 'json',
    ], text=True))
    account_key = keys[0]['value']
    endpoint = f'https://{ACCOUNT}.blob.core.windows.net'
    with BlobServiceClient(endpoint, credential=account_key) as client:
        try:
            client.create_container(CONTAINER)
        except ResourceExistsError:
            pass
        for local, key in [('models/model.joblib', 'artifacts/current/model.joblib'),
                           ('outputs/report.json', 'artifacts/current/report.json')]:
            with Path(local).open('rb') as data:
                client.get_blob_client(CONTAINER, key).upload_blob(data, overwrite=True)
    expiry = datetime.now(timezone.utc) + timedelta(days=30)
    connections = {}
    for name, permission in [
        ('local', ContainerSasPermissions(read=True, add=True, create=True, write=True, delete=True, list=True)),
        ('vm', ContainerSasPermissions(read=True)),
    ]:
        token = generate_container_sas(
            account_name=ACCOUNT, container_name=CONTAINER, account_key=account_key,
            permission=permission, start=datetime.now(timezone.utc)-timedelta(minutes=5),
            expiry=expiry, protocol='https',
        )
        connections[name] = f'AccountName={ACCOUNT};BlobEndpoint={endpoint}/;SharedAccessSignature={token}'
    env_file = Path('.env')
    values = [line for line in env_file.read_text().splitlines()
              if not line.startswith(('ARTIFACT_BUCKET=', 'AZURE_STORAGE_CONNECTION_STRING='))]
    values.extend([f'ARTIFACT_BUCKET={CONTAINER}', f"AZURE_STORAGE_CONNECTION_STRING='{connections['local']}'"])
    env_file.write_text('\n'.join(values)+'\n')
    env_file.chmod(0o600)
    vm_env = Path('.secrets/vm.env')
    vm_env.write_text(f"ARTIFACT_BUCKET={CONTAINER}\nAZURE_STORAGE_CONNECTION_STRING='{connections['vm']}'\nMODEL_PATH=/home/azureuser/models/model.joblib\n")
    vm_env.chmod(0o600)
    metadata = {
        'resource_group': GROUP, 'storage_account': ACCOUNT, 'container': CONTAINER,
        'vm': 'income-api', 'vm_size': 'Standard_B2ats_v2', 'region': 'southeastasia',
        'vm_ip': '20.212.210.172', 'vm_user': 'azureuser',
        'credentials_expire_utc': expiry.isoformat(),
        'initial_model_source': 'local MLflow experiment, F1=0.7149321266968326',
        'github_secrets_configured': False,
    }
    Path('docs/azure-resources.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print('Private container and accepted local model ready; local credentials saved securely.')
    print('No GitHub Secrets were written. SAS expiry UTC:', expiry.isoformat())


if __name__ == '__main__':
    main()
