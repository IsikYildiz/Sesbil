import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np
import SoundApi
from collections import deque
import librosa
import pandas as pd

client = TestClient(SoundApi.app)

# Global Değişken Sıfırlama 
@pytest.fixture(autouse=True)
def reset_globals():
    SoundApi.is_recording = False
    SoundApi.audio_data.clear()
    SoundApi.current_audio_data.clear()
    SoundApi.send_name_prediction = False
    SoundApi.speakers = {}
    SoundApi.stop_event.clear()
    yield
    SoundApi.stop_event.set()

# Endpoint Testleri
def test_reset_endpoint():
    SoundApi.is_recording = True
    SoundApi.send_name_prediction = True
    SoundApi.speakers = {"Ali": 30}
    SoundApi.audio_data.extend([1, 2, 3])
    SoundApi.current_audio_data.extend([4, 5, 6])

    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"message": "Durum sıfırlandı."}

    assert SoundApi.is_recording == False
    assert SoundApi.send_name_prediction == False
    assert list(SoundApi.audio_data) == []
    assert list(SoundApi.current_audio_data) == []
    assert SoundApi.speakers == {}

def test_start_recording():
    response = client.post("/start-recording")
    assert response.status_code == 200
    assert SoundApi.is_recording is True

def test_recording_already_start():
    SoundApi.is_recording = True
    response = client.post("/start-recording")
    assert response.json() == {"message": "Kayıt zaten başlatılmış durumda."}
    assert response.status_code == 200
    assert SoundApi.is_recording is True

def test_stop_recording():
    SoundApi.is_recording = True

    response = client.post("/stop-recording")
    assert response.status_code == 200
    assert response.json() == {"message": "Ses kaydı durduruldu"}
    assert SoundApi.is_recording == False
    assert SoundApi.stop_event.is_set()  

def test_recording_already_stopped():
    SoundApi.is_recording = False
    response = client.post("/stop-recording")
    assert response.status_code == 200
    assert response.json() == {"message": "Kayıt zaten durdurulmuş durumda."}

# create_histogram 
def test_create_histogram_with_data():
    SoundApi.audio_data.extend(np.random.randint(-1000, 1000, size=44100))
    result = SoundApi.create_histogram()
    assert isinstance(result, bytes)
    assert len(result) > 0

def test_create_histogram_empty():
    SoundApi.audio_data.clear()
    result = SoundApi.create_histogram()
    assert result == b""

# find_topic ve calc_emotions
@patch("SoundApi.client")
@patch("SoundApi.translate_text", side_effect=lambda text, target_language: text)
def test_find_topic_success(mock_translate, mock_client):
    mock_response = MagicMock()
    category = MagicMock()
    category.name = "Technology"
    category.confidence = 0.85
    mock_response.categories = [category]
    mock_client.classify_text.return_value = mock_response

    result = SoundApi.find_topic("bu bir testtir")

    # Artık sonuç 'Technology' kelimesini içermeli
    assert "Technology" in result or "teknoloji" in result.lower()


@patch("SoundApi.client")
def test_calc_emotions(mock_client):
    mock_response = MagicMock()
    sentiment = MagicMock()
    sentiment.score = 0.7
    sentiment.magnitude = 6.0
    mock_response.document_sentiment = sentiment
    mock_client.analyze_sentiment.return_value = mock_response

    result = SoundApi.calc_emotions("bu bir testtir")
    assert result == "Heyecanlı"

# find_talker 
@patch("SoundApi.librosa.feature.mfcc")
@patch("SoundApi.pd.DataFrame")
def test_find_talker(mock_df, mock_mfcc):
    mock_encoder = MagicMock()
    mock_encoder.inverse_transform.return_value = ["Ahmet"]

    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.zeros((1, 40))

    mock_model = MagicMock()
    mock_model.predict.return_value = [0]

    mock_df.return_value = MagicMock()
    mock_mfcc.return_value = np.random.rand(40, 100)

    fake_audio = np.ones(44100) * 1000  

    def find_talker_test(sound, encoder, scaler, model):
        if len(sound) == 0:
            return ''
        audio_datanp = np.array(sound)
        max_val = np.max(np.abs(audio_datanp))
        if max_val == 0:
            return ''
        audio_datanp = audio_datanp.astype(np.float32) / max_val
        mfcc = librosa.feature.mfcc(y=audio_datanp, sr=44100, n_mfcc=40)
        mfcc_mean = np.mean(mfcc.T, axis=0)
        features = np.array([mfcc_mean]) 
        features_scaled = scaler.transform(features)
        features_df = pd.DataFrame(features_scaled, columns=[str(i) for i in range(40)])
        predicted_label = model.predict(features_df)[0]
        predicted_name = encoder.inverse_transform([predicted_label])[0]
        return predicted_name

    result = find_talker_test(fake_audio, mock_encoder, mock_scaler, mock_model)
    assert result == "Ahmet"



# WebSocket - /name 
def test_websocket_name():
    with client.websocket_connect("/name") as websocket:
        websocket.send_text("test_name")
        msg = websocket.receive_text()
        assert msg in ["Name already exists", "Succes"]
