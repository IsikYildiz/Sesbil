from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import threading
import asyncio 
from scipy.signal import spectrogram
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

is_recording = False
audio_data = []
clients = set()
RATE = 44100

lock = threading.Lock()
stop_event = threading.Event()

def record_audio():
    global is_recording, audio_data

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    try:
        while is_recording:
            data = stream.read(CHUNK)
            audio_data.extend(np.frombuffer(data, dtype=np.int16))
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

    with lock:
        if not is_recording:
            return {"message": "Kayıt zaten durdurulmuş durumda."}

        is_recording = False
        print("Recording stopped.")
        
    stop_event.set()
    return {"message": "Ses kaydı durduruldu"}

@app.websocket("/ws/histogram")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:

            histogram = create_histogram()
            if histogram:
                await websocket.send_bytes(histogram)
                print("Histogram sent to client.")
                if not is_recording:
                    break
                
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)
    finally:
        await websocket.close()

def create_histogram():
    global audio_data

    if not audio_data:
        return b""

    #Ses verisi spektogramı yapmak için numpy dizisine dönüştürülüyor.
    audio_datanp = np.array(audio_data)
    
    #Spektogram oluşturma
    frequencies, times, Sxx = spectrogram(audio_datanp, fs=RATE)
    plt.figure(figsize=(10, 5), facecolor=(0.1686, 0.6745, 0.7882))

    #Dalga Formu
    plt.subplot(2, 1, 1)
    time_axis = np.linspace(0, len(audio_datanp) / RATE, len(audio_datanp))
    plt.plot(time_axis, audio_datanp, color='blue')
    plt.title("Data Flow (Waveform)")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Amplitüd")

    #spektogram tanımlama
    plt.subplot(2, 1, 2)
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud', cmap='viridis')
    plt.colorbar(label="Güç (dB)")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Frekans (Hz)")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png',bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer.getvalue()
