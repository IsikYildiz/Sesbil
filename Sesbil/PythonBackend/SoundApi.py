from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import threading
import asyncio 

app = FastAPI()

is_recording = False
audio_data = []
clients = set()

lock = threading.Lock()
stop_event = threading.Event()

def record_audio():
    global is_recording, audio_data

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    try:
        while is_recording:
            data = stream.read(CHUNK)
            audio_data.extend(np.frombuffer(data, dtype=np.int16))
            print(f"Captured {len(data)} bytes of audio.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

@app.post("/start-recording")
async def start_recording():
    global is_recording, audio_data

    if is_recording:
        return {"message": "Kayıt zaten başlatılmış durumda."}

    is_recording = True
    audio_data = []

    # Arka planda ses kaydını başlat
    threading.Thread(target=record_audio).start()
    return {"message": "Ses kaydı başlatıldı"}

@app.post("/stop-recording")
async def stop_recording():
    global is_recording

    if not is_recording:
        return {"message": "Kayıt zaten durdurulmuş durumda."}

    is_recording = False
    stop_event.set()
    return {"message": "Ses kaydı durduruldu"}

@app.websocket("/ws/histogram")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            if not is_recording:
                await asyncio.sleep(0.1)  # WebSocket bağlantısının direkt olarak sonlanmasını önlüyor.
                continue

            histogram = create_histogram()
            if histogram:
                await websocket.send_bytes(histogram)
                print("Histogram sent to client.")
            else:
                print("No histogram to send.")    
    except WebSocketDisconnect:
        clients.remove(websocket)
    finally:
        await websocket.close()

def create_histogram():
    global audio_data

    if not audio_data:
        print("No audio data available for histogram.")
        return b""

    plt.figure(figsize=(5, 3))
    plt.hist(audio_data, bins=50, color='blue', alpha=0.7)
    plt.title("Ses Verisi Histogramı")
    plt.xlabel("Genişlik")
    plt.ylabel("Frekans")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    print("Histogram successfully created.") 
    return buffer.getvalue()