import './elements.css'
import './site.css'
import './header.css'
import Speaking from './Speaking.png';
import SoundWawes from './SoundWawes.jpg';

function Header({children}) {
    return(
        <>
        <header>
        <div className="layered">
            <div className="layered" style={{paddingTop:"20px"}}>
                <img src={Speaking} alt="resim bulunamadı" height="150px" width="220px"/>
                <h1 className="name"> Sesbil</h1>
            </div>
            <img src={SoundWawes} alt="Resim Bulunamadı!" className="overlap"/>
        </div>
        </header>
        {children}
        </>
    )
}

export default Header