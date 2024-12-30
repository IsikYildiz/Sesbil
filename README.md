Sesbil - Ses Analiz Yazılımı

Proje Ekibi: Işık Yıldız , Hasan Yıldız 

Sesbil Projesi:

  Sesbil web tabanlı bir ses analiz projesidir. Eğer kullanıcıların proje veritabnında bir ses kaydı varsa, tek yapmaları gereken web sitesinde başlat tuşuna basıp konuşmaya başlamaktır. Kullanıcıların konuşmaları durdur tuşuna basılana kadar, 
basılmadığı müddetçe 3 dakika kadar kaydedilir. Bu sırada konuşulanların canlı olarak spektogram ve dalga formu grafikleri görülebilir, aynı zamanda konuşan kişi tahmin edilir. Konuşma durdurulduktan sonra, metne dönüştürülür ve konusu bulunur.
Aynı zamanda bu metinden kişilerin duygu durumu tahmin edilir.

Proje Mimarisi ve Kullanılan Teknolojiler:

- Projenin ön yüzü .net core çerçevesi ile yapılmıştır.
- Proje ses kaydı, histogram oluşturma gibi gereksinimleri gerçekleştirmek için python programlama dili kullanılmıştır. Python matplotlib gibi paketleriyle bu gereksinimleri kolayca karşılayabildiği için seçilmiştir.
- Proje ön ve arka yüzün bağlantısı canlı olarak veri aktarımı için Websocket ile asenkron bir şekilde yapılmıştır.   
- Sesin metne çevrilmesi, duygu durumu tahmini ve metnin konusunun çıkarılması için uygulaması kolay ve düşük maliyetli Google Speech-to-Text,Google Cloud Natural Language ve Transation Apıları kullanılmıştır.
- Konuşan kişinin tahmin edilmesi için, pythonun makine öğrenimi paketleriyle bir model oluşturulmuştur.
- Projede MySQL veri tabanı kullanılmıştır. Ses kayıtları ayrı bir dosyada olup veri tabanı sadece o dosyaların yolunu tutmaktadır.
