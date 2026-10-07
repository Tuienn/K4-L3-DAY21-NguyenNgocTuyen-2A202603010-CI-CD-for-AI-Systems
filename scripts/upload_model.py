"""Publish model and report only from the Release job, after the quality gate."""
import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient


def main():
    with BlobServiceClient.from_connection_string(os.environ["AZURE_STORAGE_CONNECTION_STRING"]) as client:
        container = client.get_container_client(os.environ["ARTIFACT_BUCKET"])
        for local, key in [
            ("models/model.joblib", "artifacts/current/model.joblib"),
            ("outputs/report.json", "artifacts/current/report.json"),
        ]:
            with Path(local).open("rb") as data:
                container.upload_blob(name=key, data=data, overwrite=True)
            print(f"Uploaded {key}")


if __name__ == "__main__":
    main()
