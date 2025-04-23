import { useState, useEffect, } from 'react';
import { useSearchParams } from 'react-router-dom';
import Map from "../components/Map";

export default function Geolocation() {

    const [searchParams] = useSearchParams();
    const [ipData, setIpData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // define an async function to fetch and parse the data
        const fetchData = async () => {
            // get the ip address from the search parameters
            const ipAddress = searchParams.get('ip');
            if (!ipAddress) {
                setError('No IP address provided');
                setLoading(false);
                return;
            }

            try {
                // get ip geolocation data from Flask API
                const response = await fetch(`http://localhost:5000/geolocationData/${ipAddress}`);
                if (!response.ok) {
                    throw new Error('HTTP error! status: ', response.status);
                }

                // get the data from the response
                const data = await response.json();
                if (!data) {
                    throw new Error('No data received from geolocation api');
                }
                setIpData(data); // update state with the geolocation data

            } catch (error) {
                console.error('Error fetching geolocation data:', error);
                setError(error.message);
            } finally {
                setLoading(false); // set loading to false when the data is fetched
            }
        };

        // call the fetchData function
        fetchData();

    }, [searchParams]);

    // early return to show loading state while data is being fetched
    if (loading) {
        return (
            <div className="geolocation-loading">
                <p>Loading . . .</p>
            </div>
        );
    }

    // display error message on screen if unable to load location data
    if (error || !ipData) {
        return (
            <div className="geolocation-error">
                <div>
                    <h2>Error</h2>
                </div>
                <div>
                    <p>{error || 'Unable to load location data'}</p>
                </div>
            </div>
        );
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