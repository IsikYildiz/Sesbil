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
        <div style={{display:"flex", paddingLeft: "25%", margin:"10px"}} className="appear">
            <input onChange={handleChange} value={name} type="text" placeholder="Bir isim giriniz" className="textfield"/>
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