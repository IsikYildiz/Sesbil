import '../../shared/elements.css'
import '../../shared/site.css'
import { useState } from 'react';

function ControlButtons({ onStart, onStop, hidden}){
    const [state,upState] = useState(0)

    const startRecord = () => {
        upState(state => state+1)
        onStart()
    }

    const stopRecord = () => {
        upState(state => state+1)
        onStop()
    }

    let content;
    if (state===0 && !hidden){
        content=(
            <>
            <button onClick={startRecord} style={{ marginLeft: "38%" }} id="Başla">Başla</button>
            </>
        )
    }
    else if (state===1 && !hidden){
        content=<button onClick={stopRecord} style={{ marginLeft: "38%" }} id="Durdur">Durdur</button>
    }

    return(
        <>
        <div style={{ display: "flex", ustifyContent: "center", gap: "20px", margin:"10px" }} className="appear">
            {content}
        </div>
        </>
    )
}

export default ControlButtons