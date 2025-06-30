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
        <div style={{alignItems:"center", justifyContent:"center"}}>
            <p>
                {head}
                &nbsp;{text}
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