export default function Navbar() {
    return (
        <nav className="navbar">
            {/* <img className="logo" src="/netara-logo-light.png" alt="Netara logo"/> */}
            <span className="title">Netara</span>
            <ul className='navbar-links'>
                <li><a href="table">Table</a></li>
                <li><a href="graphs">Graphs</a></li>
            </ul>
        </nav>
    )
}