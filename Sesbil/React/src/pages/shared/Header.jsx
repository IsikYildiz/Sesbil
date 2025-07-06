import './elements.css'
import './site.css'
import './header.css'
import Logo from './sesbil_logo.png';

function Header({children}) {
    return(
        <>
        <header>
        <div className="layered">
            <img src={Logo} alt="resim bulunamadı" height="240px" width="270px"/>
        </div>
        </header>
        {children}
        </>
    )
}

export default Header