import unittest
from SoundApi import create_histogram,translate_text,find_topic,calc_emotions
import numpy as np

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
        translate_text(text)

    def test_find_topic(self):
        text="Yakın zamanda Türkiye'de yapılan arkeolojik kazılarda daha önce bulunanlardan daha eski bir insan kafatası bulundu. Bu belkide ilk insanların Afrika değilde mezapotamyada olduğunu gösteriyor"
        result=find_topic(text)
        print(result)

    def test_calc_emotions(self):
        text="Bugün uzun aradan sonra lunaparka gitçeğimiz için çok heyecanlıyım."        
        calc_emotions(text)

if __name__ == '__main__':
    unittest.main()    