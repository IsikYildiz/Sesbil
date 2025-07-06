import '../../shared/elements.css'
import '../../shared/site.css'

function Histogram({imgData}) {
    let histogram;
    if (imgData != null){
        histogram = <img src={imgData} style={{height: "450px", 
            border: "2px solid #1A1968",
            borderRadius: "10px",
            padding:"5px",
            backgroundColor: "#0E0E0E",
            width:"100%"}} className="appear"></img>
    }
    return(
        <>
        {histogram}
        </>
    )
}

export default Histogram