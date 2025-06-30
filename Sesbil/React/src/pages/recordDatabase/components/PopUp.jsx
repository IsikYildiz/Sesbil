import '../../shared/elements.css'
import '../../shared/site.css'

function PopUp({ text, hidden, color }){
    let content;
    if(!hidden){
        content = 
        <>
        <div style={{display:"flex",justifyContent:"center",alignItems:"center",margin:"10px"}}>
            <label style={{color:color}}><b>{text}</b></label>
        </div>
        </>
    }
    return (
        <>
        {content}
        </>
    )
}

export default PopUp