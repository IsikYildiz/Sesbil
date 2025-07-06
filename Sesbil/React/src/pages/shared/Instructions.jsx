import './elements.css'

function Instructions({text,header,hidden}) {
    let head
    if (header!=null){
        head=<b>{header}: </b>
    }
    
    let content 
    if (!hidden){
        content= 
        <>
        <div style={{alignItems:"center", justifyContent:"center"}} className="appear">
            <p>
                <b style={{color:"#6a78e2"}}>{head}</b>
                {text}
            </p>
        </div>
        </>
    }
    return(
        <>
        {content}
        </>
    )
}

export default Instructions