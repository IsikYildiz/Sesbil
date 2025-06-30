import '../../shared/elements.css'
import '../../shared/site.css'

function Results({ data }) {
  return (
    <>
      {data.kisi!="" && <p id="Kişi"><b>Konuşan kişi:</b> {data.kisi}</p>}
      {data.konusanlar!="" && <p id="Konuşanlar"><b>Konuşanlar:</b> {data.konusanlar}</p>}
      {data.metin!="" && <p id="Metin"><b>Konuşulan Metin:</b> {data.metin}</p>}
      {data.konu!="" && <p id="Konu"><b>Metnin Konusu:</b> {data.konu}</p>}
      {data.duygu!="" && <p id="Duygu"><b>Konuşmacının Duygu Durumu:</b> {data.duygu}</p>}
    </>
  );
}

export default Results