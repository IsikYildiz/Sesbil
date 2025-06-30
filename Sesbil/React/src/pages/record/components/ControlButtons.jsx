import '../../shared/elements.css'
import '../../shared/site.css'
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function ControlButtons({ onStart, onStop}){
    const [state,upState] = useState(0)

    const navigate = useNavigate();
    const onSecondPage = () =>{
        navigate('/recordDatabase');
    }

    const startRecord = () => {
        upState(state => state+1)
        onStart()
    }

    const stopRecord = () => {
        upState(state => state+1)
        onStop()
    }

    let content;
    if (state===0){
        content=(
            <>
            <button onClick={startRecord} style={{ marginLeft: "22%" }} id="Başla">Başla</button>
            <button onClick={onSecondPage} style={{ marginLeft: "8%" }} id="Kaydet">Ses Kaydet</button>
            </>
        )
    }
    else if (state===1){
        content=<button onClick={stopRecord} style={{ marginLeft: "38%" }} id="Durdur">Durdur</button>
    }

    return(
        <>
        <div style={{ display: "flex", ustifyContent: "center", gap: "20px" }}>
            {content}
        </div>
        </>
    )
}

export default ControlButtons