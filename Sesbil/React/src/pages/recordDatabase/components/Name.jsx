import '../../shared/elements.css'
import '../../shared/site.css'
import { useState } from 'react';

function Name({ checkName, hidden }){
    const [name, setName] = useState('');
    
    const handleChange = (e) => {
        setName(e.target.value);
    };
    
    const handleClick = () => {
        if (name.trim() !== '') {
            checkName(name); 
        }
    };

    let content
    if(!hidden){
        content=
        <>
        <div style={{display:"flex", paddingLeft: "33%", margin:"10px"}}>
            <input onChange={handleChange} value={name} type="text" placeholder="Bir isim giriniz" style={{
                border:"2px solid rgb(35, 34, 48)",
                backgroundColor: "rgb(183, 173, 173)",
                fontSize: "20px",
                padding: "5px"
            }}/>
            <button style={{marginLeft:"8%"}} onClick={handleClick}>Gönder</button>
        </div>
        </>
    }

    return(
        <>
        {content}
        </>
    )
}

export default Name