"""Exercise API behavior without Azure, using the actual training output."""
from fastapi.testclient import TestClient
import joblib
import pandas as pd
import pytest

from src import serve
from tests.test_train import trained


@pytest.fixture
def api(trained, monkeypatch):
    _, tmp_path, _ = trained
    monkeypatch.setattr(serve, 'MODEL_PATH', tmp_path / 'models/model.joblib')
    monkeypatch.setattr(serve, 'download_model', lambda: None)
    with TestClient(serve.app) as client:
        yield client


def test_healthz(api):
    response = api.get('/healthz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_score_matches_model(api):
    model = api.app.state.model
    features = [60, 2, 5, 2, 4, 0, 1, 0, 0, 45]
    expected = int(model.predict(pd.DataFrame([features], columns=model.feature_names_in_))[0])
    response = api.post('/score', json={'features': features})
    assert response.status_code == 200
    assert response.json() == {
        'prediction': expected,
        'label': 'thu_nhap_cao' if expected else 'thu_nhap_thap',
    }


@pytest.mark.parametrize('features', [[], [0] * 9, [0] * 11])
def test_score_rejects_wrong_feature_count(api, features):
    assert api.post('/score', json={'features': features}).status_code == 400


def test_download_model_from_azure(tmp_path, monkeypatch):
    from unittest.mock import MagicMock
    monkeypatch.setenv('ARTIFACT_BUCKET', 'test-container')
    monkeypatch.setenv('AZURE_STORAGE_CONNECTION_STRING', 'test-only')
    destination = tmp_path / 'models/model.joblib'
    monkeypatch.setattr(serve, 'MODEL_PATH', destination)
    client = MagicMock()
    client.__enter__.return_value = client
    stream = client.get_blob_client.return_value.download_blob.return_value
    stream.readinto.side_effect = lambda output: output.write(b'accepted-model')
    factory = MagicMock(return_value=client)
    monkeypatch.setattr(serve.BlobServiceClient, 'from_connection_string', factory)
    serve.download_model()
    factory.assert_called_once_with('test-only')
    client.get_blob_client.assert_called_once_with(
        container='test-container', blob='artifacts/current/model.joblib',
    )
    assert destination.read_bytes() == b'accepted-model'
    assert not destination.with_suffix('.download').exists()
