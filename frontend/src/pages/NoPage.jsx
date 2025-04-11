import { Link } from 'react-router-dom';

export default function NoPage() {
    return (
        <div className="no-page-container">

            <section className="left-section">
                
                <div className="error-message">
                    <p className="error-title">Whoops . . .</p>
                    <p className="error-description">That page was not found</p>
                </div>

                <div className="error-navigation">
                    <p>Checkout some of our other pages here:</p>
                    <ul className="navigation-list">
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/tables">Tables</Link></li>
                        <li><Link to="/graphs">Graphs</Link></li>
                    </ul>
                </div>

            </section>

            <section className="right-section">
                <img src="404-page.webp" alt="page not found robot" />
            </section>

        </div>
    )
}