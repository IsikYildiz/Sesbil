# Sesbil - Ses Analiz Yazılımı / Voice Analysis Software

## Proje Ekibi / Project Team
**Işık Yıldız**, **Hasan Yıldız**

---

## 🇹🇷 Türkçe Açıklama

### Proje Özeti

**Sesbil**, web tabanlı bir ses analiz yazılımıdır. Eğer kullanıcının veritabanında bir ses kaydı varsa, tek yapması gereken web sitesinde "Başlat" tuşuna basıp konuşmaya başlamaktır. Kayıt süresi 3 dakika ile sınırlıdır veya kullanıcı "Durdur" tuşuna basana kadar devam eder.
Aynı zamanda kullanıcılar "Ses Kaydet" sayfasından, isimlerini girip seslerini kadedebilirler. Böylece ses tahmini için kullanılan model güncellenmiş olur.

**Konuşma sırasında:**
- Gerçek zamanlı **spektrogram** ve **dalga formu grafikleri** gösterilir.
- **Konuşan kişi tahmin edilir**.

**Konuşma sonrası:**
- Ses, **metne dönüştürülür**.
- **Konuşmanın konusu** belirlenir.
- Metinden **duygu durumu** tahmin edilir.

### Kullanılan Teknolojiler

- **Visual Studio Code** (geliştirme ortamı, Mac uyumu)
- **.NET Core** (frontend)
- **Python** (backend, `matplotlib` vb. kütüphaneler)
- **WebSocket** (gerçek zamanlı ön-arka yüz veri iletimi)
- **Google API'leri:**
  - Speech-to-Text
  - Cloud Natural Language
- **Makine Öğrenimi** (konuşmacı tanıma)
- **MySQL Veritabanı** (sadece ses dosya yollarını tutar)

---

## 🇬🇧 English Description

### Project Overview

**Sesbil** is a web-based voice analysis software. If the user has a voice record in the database, they simply click the **Start** button on the website and begin speaking. The recording continues for up to 3 minutes or until the **Stop** button is pressed.
Users can also record their voice by entering their name on the "Record Voice" page. This will update the model used for voice prediction.

**During speech:**
- **Real-time spectrogram** and **waveform** graphs are displayed.
- **Speaker identification** is performed live.

**After speech:**
- The audio is **converted into text**.
- The **topic** of the conversation is detected.
- **Sentiment analysis** is performed based on the text.

### Technologies Used

- **Visual Studio Code** (cross-platform, Mac compatible)
- **.NET Core** (frontend)
- **Python** (backend with libraries like `matplotlib`)
- **WebSockets** (real-time communication between frontend and backend)
- **Google APIs:**
  - Speech-to-Text
  - Cloud Natural Language
- **Machine Learning** (for speaker recognition)
- **MySQL Database** (stores only file paths of the recordings)

---
