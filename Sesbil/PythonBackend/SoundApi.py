from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import pyaudio
import numpy as np
import matplotlib
matplotlib.use('Agg')
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
from deep_translator import GoogleTranslator
import joblib
import librosa
import pandas as pd
from dotenv import load_dotenv
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from CreateModel import deploy_model

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
audio_data = deque(maxlen=RATE * 210)
current_audio_data = deque(maxlen=RATE * 10)

lock = threading.Lock()
stop_event = threading.Event()

# Ses kaydını alan fonksiyon, 10 saniyede bir global current_audio_data ve audio_data ddeğişkenlerini günceller
def record_audio():
    global is_recording, audio_data, current_audio_data,send_name_prediction

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    start=time.time()

    try:
        while is_recording:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frame = np.frombuffer(data, dtype=np.int16)
            current_audio_data.extend(frame)
            audio_data.extend(frame)
            if time.time()-start>10:
                send_name_prediction=True
                start=time.time()
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        
def record_audio_for_database():
    global is_recording, audio_data, current_audio_data,send_name_prediction

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    try:
        while is_recording:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frame = np.frombuffer(data, dtype=np.int16)
            audio_data.extend(frame)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

#Ses kaydı zaten açık değilse, ses kaydını başlatır, derekli gloabal değerleri sıfırlar ve send_name_prediction true yapar
@app.post("/start-recording")
async def start_recording():
    global is_recording, audio_data,current_audio_data,speakers,send_name_prediction

    if is_recording:
        return {"message": "Kayıt zaten başlatılmış durumda."}

    is_recording = True
    audio_data.clear()
    current_audio_data.clear()
    speakers={}
    send_name_prediction=False

    # Arka planda ses kaydını başlat
    threading.Thread(target=record_audio).start()
    return {"message": "Ses kaydı başlatıldı"}

@app.post("/start-recording-database")
async def start_recording_for_database():
    global is_recording, audio_data,current_audio_data,speakers,send_name_prediction

    if is_recording:
        return {"message": "Kayıt zaten başlatılmış durumda."}

    is_recording = True
    audio_data.clear()

    # Arka planda ses kaydını başlat
    threading.Thread(target=record_audio_for_database).start()
    return {"message": "Ses kaydı başlatıldı"}

@app.post("/stop-recording-database")
async def stop_recording_for_database(name: str):
    global is_recording

    with lock:
        if not is_recording:
            return {"message": "Kayıt zaten durdurulmuş durumda."}

        is_recording = False

    stop_event.set()

    #Ses dosyaya kaydedilir 
    audio_datanp = np.array(audio_data, dtype=np.int16)    
    voice_file_path=os.path.join(os.getenv("sesbil_voices"),name)+".wav"
    write(voice_file_path, RATE, audio_datanp)

    mongo_client=MongoClient()
    db=mongo_client["sesbil"]
    bireyler=db["bireyler"]
    new_person={"isim":name, "ses_yolu":voice_file_path}
    bireyler.insert_one(new_person)
    mongo_client.close()

    deploy_model()

    return {"message": "Ses kaydı durduruldu"}

#Ses kaydı açıksa is_recording değişkenini false yaparak, ses kaydını durdurur
@app.post("/stop-recording")
async def stop_recording():
    global is_recording

    with lock:
        if not is_recording:
            return {"message": "Kayıt zaten durdurulmuş durumda."}

        is_recording = False

    stop_event.set()
    return {"message": "Ses kaydı durduruldu"}

@app.websocket("/name")
async def checkName(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    mongo_client=MongoClient()
    db=mongo_client["sesbil"]
    bireyler=db["bireyler"]

    try:
        name=await websocket.receive_text()
        if bireyler.find_one({"isim": name}):
            await websocket.send_text("Name already exists") 
        else:
            await websocket.send_text("Succes") 
    except WebSocketDisconnect:
        mongo_client.close()
        clients.remove(websocket)



#Websocket bağlantısı ile frontend e gerekli bilgiler gönderilir
@app.websocket("/information")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    global audio_data, current_audio_data, send_name_prediction, speakers, is_recording

    #Makine öğrenimi modelini yükler
    encoder=joblib.load("label_encoder.pkl")
    scaler=joblib.load("scaler.pkl")
    model=joblib.load("voice_recognition_model.joblib")

    start=time.time()
    
    executor = ThreadPoolExecutor(max_workers=4)

    try:
        while True:
            #sürekli olarak verilerden histogram oluşturur
            loop = asyncio.get_event_loop()
            
            if time.time()-start>0.5:
                histogram = await loop.run_in_executor(executor, create_histogram)
                await websocket.send_bytes(histogram)
                start = time.time()

            #send_name_prediction true ise kullanıcıyı tahmin eder ve tahmini + toplam tahmin istatisliklerini (güncelleyerek) gönderir
            if send_name_prediction:
                predicted_name=find_talker(current_audio_data,encoder,scaler,model)
                current_audio_data.clear()
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
                    audio_data.clear()
                    current_audio_data.clear()
                    speakers={}

                    await websocket.close()
                break

            await asyncio.sleep(0.01)

    #WebSocket bağlantısı önceden kesilirse global değişkenler sıfırlanır, ve geçici ses dosyası silinir
    except WebSocketDisconnect:
        if os.path.exists("geçiciDosya.wav"):
            os.remove("geçiciDosya.wav")
        audio_data.clear()
        current_audio_data.clear()
        speakers={}
        is_recording=False
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
    time_axis = np.arange(0, len(audio_datanp)) / RATE
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
        try:
            text = recognizer.recognize_google(audio_data, language="tr-TR")  # Türkçe için "tr-TR" kullan
        except sr.UnknownValueError:
            return 'Ses anlaşılamadı'
        
    return text  

#Konu analizi için metni ingilizceye ve türkçeye çevirme
def translate_text(text, target_language):
    result = GoogleTranslator(source='auto', target_language=target_language).translate(text=text)
    return result

#Konuyu bulma
def find_topic(text):
    if text=='Ses anlaşılamadı':
        return 'Ses metne çevirelemedi'
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
    if text=='Ses anlaşılamadı':
        return 'Ses metne çevirelemedi'
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
    mfcc=librosa.feature.mfcc(y=audio_datanp,sr=RATE,n_mfcc=40)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    features=[]
    features.append(mfcc_mean)
    features_scaled=scaler.transform(features)
    features_df = pd.DataFrame(features_scaled, columns=[str(i) for i in range(40)])    
    predicted_label=model.predict(features_df)[0]
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