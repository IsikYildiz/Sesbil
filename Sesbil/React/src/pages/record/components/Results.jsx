import '../../shared/elements.css'
import '../../shared/site.css'
import PieChart from'./PieChart.jsx'
import Excited from '../../shared/emotions/Excited.png'
import VeryHappy from '../../shared/emotions/Very Happy.png'
import Happy from '../../shared/emotions/Happy.png'
import Calm from '../../shared/emotions/Calm.png'
import Unhappy from '../../shared/emotions/Unhappy.png'
import Angry from '../../shared/emotions/Angry.png'
import VeryAngry from '../../shared/emotions/Very Angry.png'
import VeryUnhappy from '../../shared/emotions/Very Unhappy.png'
import Netural from '../../shared/emotions/Netural.png'

function Results({ data }) {
  let content, emotionImg=null;

  switch (data.duygu) {
  case "Heyecanlı":
    emotionImg=Excited
    break;
  case "Oldukça mutlu":
    emotionImg=VeryHappy
    break;
  case "Mutlu":
    emotionImg=Happy
    break;
  case "Sakin":
    emotionImg=Calm
    break;
  case "Mutsuz":
    emotionImg=Unhappy
    break;
  case "Sinirli":
    emotionImg=Angry
    break;
  case "Aşırı öfkeli":
    emotionImg=VeryAngry
    break;
  case "Oldukça mutsuz":
    emotionImg=VeryUnhappy
    break;
  default:
    emotionImg=Netural
    data.duygu="Nötr"
  }

  function parseSpeakerString(input) {
    if (!input) return [];
    // Köşeli parantezleri ve boşlukları temizle
    input = input.replace(/[\[\]{}']/g, '').trim();
    
    // Virgülle ayır → her bir öğe "Ali:20s" gibi olacak
    const parts = input.split(',');

    const result = parts.map(item => {
      const [name, valueWithS] = item.trim().split(':');
      const value = parseInt(valueWithS.replace('s', ''));
      return {
        id: name,
        label: name,
        value: value
      };
    });
    return result;
  }

  function parseTopicString(input) {
    if (!input) return [];
    const parts = input.split(',');
    
    const result = parts.map(item => {
      const [topic, percentStr] = item.trim().split(':');
      const percent = parseFloat(percentStr.replace('%', ''));
      
      return {
        id: topic,
        label: topic,
        value: percent
      };
    });
    return result;
  }


  if(data.metin==""){
    content=
    <>
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      {data.kisi!="" && <p id="Kişi" style={{marginTop:"20px"}}><b>Konuşan kişi:</b> {data.kisi}</p>}
      {data.konusanlar!="" && <p id="Konuşanlar" style={{marginTop:"20px"}}><b>Konuşanlar:</b> {data.konusanlar}</p>}
    </div>
    </>
  }
  else{
    const konusanlar=parseSpeakerString(data.konusanlar)
    const konular=parseTopicString(data.konu)
    content=
    <>
    <div style={{ display: "flex", flexDirection: "column", width:"1000px"}}>
      {data.metin!="" && <p style={{width:"1000px"}}><b>Konuşulan Metin:</b> {data.metin}</p>}
      <div style={{display:"flex", marginTop:"40px"}}>
        <div className="resultbox">
          <PieChart data={konusanlar}/>
        </div>
        <div className="resultbox">
          <PieChart data={konular}/>
        </div>
        <div className="resultbox" style={{marginRight:"0"}}>
          <img src={emotionImg} style={{width:"125px",height:"125px"}}></img>
          <div style={{ fontFamily: "'Ligconsolata'", color: 'white', fontSize: '22px', textAlign: 'center', marginTop:"20px" }}>Duygu Durumu: {data.duygu}</div>       
        </div>
      </div>
    </div>
    </>
  }
  
  return (
    <>
    {content}
    </>
  );
}

export default Results