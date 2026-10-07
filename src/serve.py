"""Azure Blob-backed Adult income inference API."""
from contextlib import asynccontextmanager
import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from fastapi import FastAPI, HTTPException, Request
import joblib
import pandas as pd
from pydantic import BaseModel, ConfigDict

MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", "~/models/model.joblib")).expanduser()


def download_model():
    """Download the accepted model atomically; errors prevent API startup."""
    container = os.environ["ARTIFACT_BUCKET"]
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = MODEL_PATH.with_suffix(".download")
    try:
        with BlobServiceClient.from_connection_string(connection_string) as client:
            blob = client.get_blob_client(container=container, blob=MODEL_KEY)
            with temporary_path.open("wb") as output:
                blob.download_blob().readinto(output)
        temporary_path.replace(MODEL_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)
    print("Downloaded accepted model from Azure Blob Storage")


@asynccontextmanager
async def lifespan(app):
    download_model()
    app.state.model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(lifespan=lifespan)


class ScoreRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    features: list[float]


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest, request: Request):
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")
    model = request.app.state.model
    features = pd.DataFrame([req.features], columns=model.feature_names_in_)
    prediction = int(model.predict(features)[0])
    return {
        "prediction": prediction,
        "label": "thu_nhap_cao" if prediction == 1 else "thu_nhap_thap",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
