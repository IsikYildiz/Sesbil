import '../../shared/elements.css'
import '../../shared/site.css'

function Histogram({imgData}) {
    let histogram;
    if (imgData != null){
        histogram = <img src={imgData} style={{height: "450px", 
            border: "2px solid black",
            borderRadius: "10px",
            backgroundColor: "rgb(207, 204, 204)",
            width:"100%"}}></img>
    }
    return(
        <>
        {histogram}
        </>
    )
}

export default Histogram