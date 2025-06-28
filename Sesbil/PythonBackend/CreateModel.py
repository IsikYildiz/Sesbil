import librosa
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd
import joblib
import time
from pymongo import MongoClient
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import joblib 
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis



def get_database_data():
    #Veri tabanına bağlanma
    client = MongoClient()
    db=client["sesbil"]
    bireyler_collection=db["bireyler"]

    labels=[]
    features=[]
    segment_duration=10  

    #Verilerden kişi isimleri ve ses özellikleri alınır. Veri seti daha küçük parçalara bölünür.
    for person in bireyler_collection.find():
        audio, sample_rate=librosa.load(person["ses_yolu"])
        segment_samples = segment_duration * sample_rate
        num_segments = len(audio) // segment_samples
        for i in range(num_segments):
            labels.append(person["isim"])
            start = i * segment_samples
            end = start + segment_samples
            segment = audio[start:end]
            mfcc=librosa.feature.mfcc(y=segment,sr=sample_rate,n_mfcc=40)
            mfcc_mean = np.mean(mfcc.T, axis=0)  
            features.append(mfcc_mean)
    
    client.close()

    return labels, features

def preprocess_data():
    labels, features=get_database_data()

    #Kişiler sayısallaştırılır
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    joblib.dump(label_encoder, "label_encoder.pkl")
    
    #Veriler normalize edilir
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)
    joblib.dump(scaler, "scaler.pkl")

    # Özellikler ve etiketleri pandas DataFrame'ine dönüştürüyoruz
    df = pd.DataFrame(features_normalized)  # Özellikleri DataFrame'e dönüştürüyoruz
    df['label'] = encoded_labels  # Etiketleri ekliyoruz
    df.to_csv("ses.csv", index=False)

def deploy_model():
    preprocess_data()
    df = pd.read_csv('ses.csv')
    x=df.iloc[:, :-1]
    y=df["label"]
    
    models = [
        ("KNN", KNeighborsClassifier()),
        ("SVC", SVC()),
        ("RandomForestClassifier", RandomForestClassifier()),
        ("LogisticRegression", LogisticRegression(max_iter=1000)),
        ("MLPClassifier", MLPClassifier(max_iter=1000)),
        ("CatBoost", CatBoostClassifier(verbose=0)),
        ("LDA", LinearDiscriminantAnalysis())
    ]
    
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    
    best_accuracy=0
    best_time=10
    results=[]

    #En iyi model seçiliyor
    for name, model in models:
        start_time = time.time()
        
        model.fit(x_train, y_train)  
        y_pred = model.predict(x_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        end_Time=time.time()-start_time

        results.append({
            "Algoritma": name,
            'Doğruluk': accuracy,
            'Zaman (s)': end_Time
        })
        
        if accuracy > best_accuracy or (accuracy == best_accuracy and end_Time < best_time):
            best_accuracy = accuracy
            best_time = end_Time
            joblib.dump(model, "voice_recognition_model.joblib")

deploy_model()