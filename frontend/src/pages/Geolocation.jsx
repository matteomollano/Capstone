import { useState, useEffect, } from 'react';
import Map from "../components/Map";

export default function Geolocation() {

    const [ipData, setIpData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // define an async function to fetch and parse the data
        const fetchData = async () => {
            try {
                const storedData = sessionStorage.getItem('ipData');

                if (storedData) {
                    const parsedData = JSON.parse(storedData);
                    setIpData(parsedData); // update the state variable with the parsed data
                } else {
                    console.error('No ipData found in sessionStorage');
                }
            } catch (error) {
                console.error('Error parsing ipData:', error);
            } finally {
                setLoading(false); // set loading to false when the data is fetched
            }
        };

        // call the fetchData function
        fetchData();

        // clean up: remove the data from sessionStorage after fetching
        return () => sessionStorage.removeItem('ipData');
    }, []); // empty dependency array means this will run only once after the first render

    // early return to show loading state while data is being fetched
    if (loading) {
        return <div>Loading...</div>;
    }

    // deconstruct ipData object into variables
    const {
        ip,
        city,
        region,
        country_name: country,
        continent_name: continent,
        latitude,
        longitude,
        flag,
        asn: { route: subnet, name: company, domain }
    } = ipData;

    return (
        <div className="geolocation-container">
            <div className="map-section">
                {/* ensure latitude and longitude are valid before passing to Map */}
                {latitude && longitude ? (
                    <Map latitude={latitude} longitude={longitude} />
                ) : (
                    <div>Map data unavailable</div>
                )}
            </div>

            <div className="domain-info-section">
                <div className="grid-container">
                    
                    <div className="info-div">
                        <p className="info-header">IP</p>
                        <p className="info-data">{ip ? ip : 'N/A'}</p>
                    </div>

                    <div className="info-div">
                        <p className="info-header">Subnet</p>
                        <p className="info-data">{subnet ? subnet : 'N/A'}</p>
                    </div>

                    <div className="info-div">
                        <p className="info-header">Company</p>
                        <p className="info-data">{company ? company : 'N/A'}</p>
                    </div>

                    <div className="info-div">
                        <p className="info-header">Domain</p>
                        {ipData?.asn?.domain ? (
                            <a className="info-data-link" href={`https://${domain}`}
                                target="_blank" rel="noopener noreferrer">{domain}</a>
                        ) : (
                            'N/A'
                        )}
                    </div>

                    <div className="info-div">
                        <p className="info-header">City</p>
                        <p className="info-data">{city ? city : 'N/A'}</p>
                    </div>

                    <div className="info-div">
                        <p className="info-header">State</p>
                        <p className="info-data">{region ? region : 'N/A'}</p>
                    </div>
                    
                    <div className="info-div">
                        <p className="info-header">Country</p>
                        <div className="image-container">
                            <img class="flag-image" src={flag} alt={`flag of ${country}`} />
                            <p className="info-data">{country ? country : 'N/A'}</p>
                        </div>
                    </div>

                    <div className="info-div">
                        <p className="info-header">Continent</p>
                        <p className="info-data">{continent ? continent : 'N/A'}</p>
                    </div>

                </div>
            </div>
        </div>
    )
}