from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import threading
import asyncio 
from scipy.signal import spectrogram
from scipy.io.wavfile import write
import speech_recognition as sr
import os
import time
from google.cloud import language_v1
from google.cloud import translate_v2 as translate
import joblib
import librosa
import pandas as pd
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("google_api")
client = language_v1.LanguageServiceClient()

is_recording = False
send_name_prediction=False
audio_data = []
current_audio_data=[]
speakers={}
clients = set()
RATE = 44100

lock = threading.Lock()
stop_event = threading.Event()

def record_audio():
    global is_recording, audio_data, current_audio_data,send_name_prediction

    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    start=time.time()

    try:
        while is_recording:
            data = stream.read(CHUNK)
            audio_data.extend(np.frombuffer(data, dtype=np.int16))
            current_audio_data.extend(np.frombuffer(data, dtype=np.int16))
            if time.time()-start>11:
                send_name_prediction=True
                current_audio_data=[]
                start=time.time()
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

@app.post("/start-recording")
async def start_recording():
    global is_recording, audio_data,current_audio_data

    if is_recording:
        return {"message": "Kayıt zaten başlatılmış durumda."}

    is_recording = True
    audio_data = []
    current_audio_data=[]

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

    stop_event.set()
    return {"message": "Ses kaydı durduruldu"}

#Websocket bağlantısı ile frontend e gerekli bilgiler gönderilir
@app.websocket("/ws/information")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    global audio_data, current_audio_data, send_name_prediction, speakers

    encoder=joblib.load("label_encoder.pkl")
    scaler=joblib.load("scaler.pkl")
    model=joblib.load("best_model.joblib")

    start=time.time()

    try:
        while True:
            if time.time()-start>0.5:
                histogram = create_histogram()
                await websocket.send_bytes(histogram)
                print("Histogram sent to client.")
                start=time.time()

            if send_name_prediction:
                predicted_name=find_talker(current_audio_data,encoder,scaler,model)
                name="dördüncü mesaj" + predicted_name
                await websocket.send_text(name)

                statistics='beşinci mesaj'+speaker_statistic(predicted_name)
                await websocket.send_text(statistics)

                send_name_prediction=False

            if not is_recording:
                if audio_data:   
                    #Ses dosyaya kaydedilir 
                    audio_datanp = np.array(audio_data, dtype=np.int16)    
                    write("geçiciDosya.wav", RATE, audio_datanp)
                    
                    #Ses dosyası metne dönüştürülür
                    speech_text=speech_to_text("geçiciDosya.wav")
                    send_sppech_text="ilk mesaj"+speech_text
                    await websocket.send_text(send_sppech_text)    

                    #Metin üzerinden konu bulunur
                    topic="ikinci mesaj"+ str(find_topic(speech_text))
                    await websocket.send_text(topic)

                    #Metin üzerinden duygu bulunur
                    emotion="üçüncü mesaj"+calc_emotions(speech_text)
                    await websocket.send_text(emotion)

                    #Bilgiler sıfırlanır
                    os.remove("geçiciDosya.wav")
                    audio_data=[]
                    current_audio_data=[]
                    speakers=[]

                    await websocket.close()
                break

            await asyncio.sleep(0.001)
    except WebSocketDisconnect:
        clients.remove(websocket)

#Spektogram ve dalga formu oluşturulur
def create_histogram():
    global audio_data

    if not audio_data:
        return b""

    #Ses verisi spektogramı yapmak için numpy dizisine dönüştürülüyor
    audio_datanp = np.array(audio_data)
    
    #Spektogram oluşturma
    frequencies, times, Sxx = spectrogram(audio_datanp, fs=RATE)
    plt.figure(figsize=(10, 5), facecolor=(0.1686, 0.6745, 0.7882))

    #Dalga Formu
    plt.subplot(2, 1, 1)
    time_axis = np.linspace(0, len(audio_datanp) / RATE, len(audio_datanp))
    plt.plot(time_axis, audio_datanp, color='blue')
    plt.title("Dalga Formu")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Amplitüd")

    #spektogram tanımlama
    plt.subplot(2, 1, 2)
    Sxx[Sxx == 0] = 1e-10
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud', cmap='viridis')
    plt.colorbar(label="Güç (dB)")
    plt.xlabel("Zaman (s)")
    plt.ylabel("Frekans (Hz)")
    plt.tight_layout()

    #Oluşturulan grafikler gönderilir
    buffer = BytesIO()
    plt.savefig(buffer, format='png',bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer.getvalue()

#Konuşmayı yazıya çevirme
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="tr-TR")  # Türkçe için "tr-TR" kullan
    return text  

#Konu analizi için metni ingilizceye ve türkçeye çevirme
def translate_text(text, target_language):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result["translatedText"]

#Konuyu bulma
def find_topic(text):
    text=translate_text(text,'en')
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)

    #Konu sınıflandırması yapılır
    response = client.classify_text(document=document)

    #Konu kategorileri kaydedilir ve sonra döndürülür
    topics = []
    for category in response.categories:
        topics.append({
            "Category": category.name,
            "Trust": f"{category.confidence * 100:.2f}%"
        }) 

    if topics==[]:
        return 'Belirli bir kategori bulunamadı'   
    else: 
        topics=str(topics)
        table=dict.fromkeys(map(ord,'{[]}\''),None)
        topics=topics.translate(table)
        topics=translate_text(topics,'tr')
        print(topics)
        return topics

#Metinden duyguyu analiz etme
def calc_emotions(text):
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)

    #Duygu analizi yap
    sentiment_response = client.analyze_sentiment(document=document)

    #Sonuçları döndür
    sentiment = sentiment_response.document_sentiment
    duygu = ""

    # Duygu belirleme (puan ve büyüklüğe göre daha ayrıntılı duygular)
    if sentiment.score > 0.6:
        if sentiment.magnitude > 5:
            duygu="Heyecanlı"
        elif 3 < sentiment.magnitude < 5:
            duygu="Oldukça mutlu"
        else:
            duygu="Mutlu"    
    elif 0.4 < sentiment.score <= 0.6:
        if sentiment.magnitude > 2:
            duygu="Mutlu"
        else:
            duygu="Sakin"
    elif -0.5 < sentiment.score < 0:
        if sentiment.magnitude > 3:
            duygu="Sinirli"
        else:
            duygu="Mutsuz"    
    elif sentiment.score <= -0.5:
        if sentiment.magnitude > 3:
            duygu="Aşırı öfkeli"
        else:
            duygu="Oldukça mutsuz"    
    else:
        duygu="Nötr"

    return duygu

#Ses verisi modelden geçirilerek kişi tahmini yapılır
def find_talker(sound,encoder,scaler,model):
    if sound==[]:
        return ''
    audio_datanp = np.array(sound)
    audio_datanp=audio_datanp.astype(np.float32) / np.max(np.abs(audio_datanp))
    mfcc=librosa.feature.mfcc(y=audio_datanp,sr=RATE,n_mfcc=20)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    features=[]
    features.append(mfcc_mean)
    features_scaled=scaler.transform(features)
    columns_to_remove = [1, 13]
    remaining_features = np.delete(features_scaled, columns_to_remove, axis=1)
    remaining_features_df=pd.DataFrame(remaining_features,columns=["0","2","3","4","5","6","7","8","9","10","11","12","14","15","16","17","18","19"])
    predicted_label=model.predict(remaining_features_df)[0]
    predicted_name = encoder.inverse_transform([predicted_label])[0]
    
    return predicted_name

def speaker_statistic(name):
    global speakers

    if name in speakers:
        speakers[name]+=10
    else:
        speakers[name]=10

    speakers_list=[]   
    for name in speakers:
        speakers_list.append(name+':'+str(speakers[name])+'s')
        
    speakers_str=str(speakers_list)
    table=dict.fromkeys(map(ord,'{[]}\''),None)
    speakers_str=speakers_str.translate(table)

    return speakers_str