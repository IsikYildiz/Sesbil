import '../shared/elements.css'
import '../shared/site.css'
import React, { useRef, useState, useEffect } from 'react'
import Instructions from '../shared/Instructions.jsx'
import DatabaseControlButtons from './components/DatabaseControlButtons.jsx'
import Name from './components/Name.jsx'
import PopUp from './components/PopUp.jsx'
import { useNavigate } from 'react-router-dom';

function RecordDatabase() {
    const socketRef = useRef(null);

    const [instruction,setInstructionsData] = useState({
        text:`İlk öncelikle bir isim giriniz. 
        Ardından Başla tuşuna basıp sesinizi max 3dk kaydedebilirsiniz.
        Tahminin doğruluğunun yüksek olması için en az 1dk Kayıt önerilir.
        Ses kaydını durdurmak için durdur tuşuna basın ve sessizce bekleyin. 
        Daha sonra ana sayfadan devam edebilirsiniz.`,
        header:"Ses Ekleme",
        hidden:false
    })

    const [popUp,setPopUpData] = useState ({
        text:"Bu isim zaten kayıtlıdır!",
        hidden:true,
        color:"red"
    })

    const [nameHidden,setNameVisibility] = useState(false)

    const [name,setName] = useState(null)

    const [buttonHidden,setButtonBVisibility] = useState(true)

    async function checkName(name){
        if (!name) {
            setPopUpData(prev => ({...prev, text:"Lütfen bir isim giriniz!"}))
            setPopUpData(prev => ({...prev, hidden:false}))
            setPopUpData(prev => ({...prev, color:"red"}))
            return;
        }

        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            console.warn("WebSocket already open.");
            return;
        }

        const socket = new WebSocket("ws://127.0.0.1:8000/name");
        socketRef.current = socket;

        socket.onopen = function () {
            socket.send(name);
        };

        socket.onmessage = function (event) {
            if (event.data === "Succes") {
                setPopUpData(prev => ({...prev, text:"Başarılı!"}))
                setPopUpData(prev => ({...prev, hidden:false}))
                setPopUpData(prev => ({...prev, color:"green"}))
                setNameVisibility(prev => !prev)
                setButtonBVisibility(prev => !prev)
                setName(prev => prev=name)
                socket.close()
            } 
            else {
                setPopUpData(prev => ({...prev, text:"Bu isim zaten kayıtlıdır!"}))
                setPopUpData(prev => ({...prev, hidden:false}))
                setPopUpData(prev => ({...prev, color:"red"}))
                socket.close();
            }
        }

        socket.onclose = () => {
            console.log("WebSocket kapandı.");
        };
    }

    async function startRecordingDatabase() {
        setInstructionsData(prev => ({...prev, text:"Sesiniz şuan kaydediliyor..."}))
        setInstructionsData(prev => ({...prev, header:null}))
        setPopUpData(prev => ({...prev, hidden:true}))

        await fetch('http://localhost:5020/api/recording/start-database', { method: 'POST' });

        setTimeout(() => stopRecordingDatabase(), 180000);
    }

    async function stopRecordingDatabase() {
        setInstructionsData(prev => ({...prev, hidden:true}))
        setPopUpData(prev => ({...prev, text:"Başarılı!"}))
        setPopUpData(prev => ({...prev, hidden:false}))
        setPopUpData(prev => ({...prev, color:"green"}))

        await fetch("http://localhost:5020/api/recording/stop-database?name="+name+"", { method: 'POST' });

        setTimeout(()=> goHomePage(),3000);
    }

    const navigate = useNavigate();
    const goHomePage = () =>{
        navigate('/');
    }

    useEffect(() => {
        // ilk yüklendiğinde yenile
        fetch('http://localhost:5020/api/recording/reset', { method: 'POST' });
    }, []);

    return(
        <>
        <div style={{width:"800px"}}>
        <Instructions text={instruction.text}
        header={instruction.header}
        hidden={instruction.hidden}/>
        <PopUp text={popUp.text} hidden={popUp.hidden} color={popUp.color}/>
        <Name hidden={nameHidden} checkName={checkName}/>
        <DatabaseControlButtons hidden={buttonHidden} onStart={startRecordingDatabase} onStop={stopRecordingDatabase}/>
        </div>
        </>
    )
}

export default RecordDatabase