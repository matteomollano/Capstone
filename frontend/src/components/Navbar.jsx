import { Link } from 'react-router-dom';

export default function Navbar() {
    return (
        <nav className="navbar">
            {/* <img className="logo" src="/netara-logo-light.png" alt="Netara logo"/> */}
            <span className="title">Netara</span>
            <ul className='navbar-links'>
                <li><Link to="/">Home</Link></li>
                <li><Link to="/table">Table</Link></li>
                <li><Link to="/graphs">Graphs</Link></li>
            </ul>
        </nav>
    )
}