import unittest
from SoundApi import translate_text,find_topic,calc_emotions
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from scipy.signal import spectrogram

def create_histogram(audio_data):
        if not audio_data:
            return b""
        
        RATE=440
        
        audio_datanp = np.array(audio_data)
        frequencies, times, Sxx = spectrogram(audio_datanp, fs=RATE)
        plt.figure(figsize=(10, 5), facecolor=(0.1686, 0.6745, 0.7882))
        plt.subplot(2, 1, 1)
        time_axis = np.linspace(0, len(audio_datanp) / RATE, len(audio_datanp))
        plt.plot(time_axis, audio_datanp, color='blue')
        plt.title("Dalga Formu")
        plt.xlabel("Zaman (s)")
        plt.ylabel("Amplitüd")
        plt.subplot(2, 1, 2)
        Sxx[Sxx == 0] = 1e-10
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

class Unit_Tests(unittest.TestCase):
    def test_histogram_output(self):
        samplerate = 44100 
        duration = 1 
        frequency = 440 
        
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        audio_data = np.sin(2 * np.pi * frequency * t)  
        audio_data = np.int16(audio_data * 32767)  
        audio_bytes = audio_data.tolist()

        create_histogram(audio_bytes)
    
    def test_histogram_no_sound(self):
        audio=None
        result=create_histogram(audio)
        self.assertEqual(b"",result)

    def test_translate_text(self):
        text="Yarın hava güneşli olacak"
        result=translate_text(text,'en')
        print(result)

    def test_find_topic(self):
        text="Yakın zamanda Türkiye'de yapılan arkeolojik kazılarda daha önce bulunanlardan daha eski bir insan kafatası bulundu. Bu belkide ilk insanların Afrika değilde mezapotamyada olduğunu gösteriyor"
        find_topic(text)

    def test_calc_emotions(self):
        text="Bugün uzun aradan sonra lunaparka gitçeğimiz için çok heyecanlıyım."        
        result=calc_emotions(text)  
        print(result)

if __name__ == '__main__':
    unittest.main()    