import '../shared/elements.css'
import '../shared/site.css'
import Instructions from '../shared/Instructions.jsx'
import Results from './components/Results.jsx'
import Histogram from './components/Histogram.jsx'
import ControlButtons from './components/ControlButtons.jsx'
import Speaking from '../shared/Speaking.png'
import React, { useRef, useState, useEffect } from 'react'

function Record(){
    const socketRef = useRef(null); // websocket bağlantısı
    const [data, setData] = useState({
        metin: "",
        konu: "",
        duygu: "",
        kisi: "",
        konusanlar: ""
    });

    const [histogram, setHistogram] = useState(null);

    const [instructionsVisibility, setInstructionsVisibility] = useState(false)

    const [speakingVisibility, setSpeakingVisiblity] = useState(true)

    useEffect(() => {
        // ilk yüklendiğinde reset at
        fetch('http://localhost:5020/api/recording/reset', { method: 'POST' });
    }, []);

    async function startRecording() {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            console.warn("WebSocket already open.");
            return;
        }

        setSpeakingVisiblity(prev => !prev)

        await fetch('http://localhost:5020/api/recording/start', { method: 'POST' });

        const socket = new WebSocket("ws://127.0.0.1:8000/information");
        socketRef.current = socket;

        setInstructionsVisibility(prev => !prev)

        socket.onmessage = (event) => {
            const message = event.data;

            if (typeof message === "string") {
                if (message.includes("ilk mesaj")) {
                    setData(prev => ({ ...prev, metin: message.substring("İlk mesaj".length) }));
                    setHistogram(null);
                } else if (message.includes("ikinci mesaj")) {
                    setData(prev => ({ ...prev, konu: message.substring("ikinci mesaj".length) }));
                } else if (message.includes("üçüncü mesaj")) {
                    setData(prev => ({ ...prev, duygu: message.substring("üçüncü mesaj".length) }));
                } else if (message.includes("dördüncü mesaj")) {
                    setData(prev => ({ ...prev, kisi: message.substring("dördüncü mesaj".length) }));
                } else if (message.includes("beşinci mesaj")) {
                    setData(prev => ({ ...prev, konusanlar: message.substring("beşinci mesaj".length) }));
                }
            } else if (message instanceof Blob || message instanceof ArrayBuffer) {
                const blob = message instanceof Blob ? message : new Blob([new Uint8Array(message)], { type: 'image/png' });
                setHistogram(URL.createObjectURL(blob));
            } else {
                console.error("Beklenmeyen veri türü:", typeof message);
            }
        };

        socket.onclose = () => {
            console.log("WebSocket kapandı.");
        };

        // 3dk sonra otomatik kapat
        setTimeout(stopRecording, 180000);
    }

    async function stopRecording() {
        await fetch('http://localhost:5020/api/recording/stop', { method: 'POST' });
    }

    let speakingImg;
    if (speakingVisibility){
        speakingImg=<img src={Speaking} style={{width:"280px", height:"240px", marginRight:"100px", marginTop:"50px", display:{speakingVisibility}}} className="appear"/>
    }

    return(
        <>
        <div style={{display:"flex", justifyContent: "center", width: "100%"}}>
            {speakingImg}          
            <div style={{width:"1000px"}}>
            <Instructions text="Tek yapmanız gereken başla tuşuna basıp konuşmaktır. 
            Maksimum 3dk konuşabilirsiniz, konuştuğunuz süre boyunca kimin konuştuğu tahmin edilecektir.
            Ses kaydını durdurmak için durdur tuşuna basıp sessizce bekleyin. 
            Konuşmanız metne dönüştürülecek, konuşmanın konusu bulunacak ve duygu tahmini yapılacaktır. 
            Eğer konuşmalarınız 25 kelimeden az ise konu belirleme ve duygu tahmini yapılamaz."
            header="Nasıl Kullanılır"
            hidden={instructionsVisibility} />
            <Histogram imgData={histogram} className="appear"/>
            <ControlButtons onStart={startRecording} onStop={stopRecording} />
            <Results data={data} className="appear" style={{marginTop:"59px"}}/>
            </div>
        </div>
        </>
    )
}

export default Record