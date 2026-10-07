"""Write the lab credentials to GitHub only with the user's explicit authorization."""
from pathlib import Path
import json
import subprocess

from dotenv import dotenv_values

REPO = 'Tuienn/K4-L3-DAY21-NguyenNgocTuyen-2A202603010-CI-CD-for-AI-Systems'


def main():
    local = dotenv_values('.env')
    resources = json.loads(Path('docs/azure-resources.json').read_text())
    secrets = {
        'STORAGE_CREDENTIALS': local['AZURE_STORAGE_CONNECTION_STRING'],
        'ARTIFACT_BUCKET': local['ARTIFACT_BUCKET'],
        'SERVER_HOST': resources['vm_ip'],
        'SERVER_USER': resources['vm_user'],
        'SERVER_SSH_KEY': Path('.secrets/income_deploy').read_text(),
    }
    for name, value in secrets.items():
        if not value:
            raise ValueError(f'Missing value for {name}')
        subprocess.run(['gh', 'secret', 'set', name, '--repo', REPO],
                       input=value, text=True, check=True, stdout=subprocess.DEVNULL)
    fingerprint = subprocess.check_output(
        ['ssh-keygen', '-lf', '.secrets/known_hosts'], text=True,
    ).split()[1]
    subprocess.run(['gh', 'variable', 'set', 'SERVER_HOST_FINGERPRINT', '--repo', REPO],
                   input=fingerprint, text=True, check=True, stdout=subprocess.DEVNULL)
    resources['github_secrets_configured'] = True
    Path('docs/azure-resources.json').write_text(json.dumps(resources, indent=2)+'\n')
    print('Configured 5 GitHub Secrets and SSH server fingerprint; no secret values printed.')


if __name__ == '__main__':
    main()
