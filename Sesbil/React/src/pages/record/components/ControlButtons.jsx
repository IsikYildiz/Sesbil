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
            <div style={{ display: "flex", alignItems:"center", justifyContent:"center", gap: "20px", width:"800px"}} className="appear">
            <button onClick={startRecord} style={{ marginRight:"20px", marginTop:"40px" }} id="Başla">Başla</button>
            <button onClick={onSecondPage} style={{ marginTop:"40px" }} id="Kaydet">Ses Kaydet</button>
            </div>
            </>
        )
    }
    else if (state===1){
        content=(
            <div style={{ display: "flex", alignItems:"center", justifyContent:"center", gap: "20px", width:"1000px"}} className="appear">
                <button onClick={stopRecord} style={{marginTop:"30px"}} id="Durdur">Durdur</button>
            </div>
        )
    }

    return(
        <>
        {content}
        </>
    )
}

export default ControlButtons