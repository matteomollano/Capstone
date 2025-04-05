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

    // extract latitude and longitude from the ipData
    const latitude = ipData?.latitude;
    const longitude = ipData?.longitude;

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
                <p>IP data will go here</p>
                <p>More data</p>
                {/* display ip info here */}
                <p>IP Address: {ipData?.ip}</p>
                <p>Subnet: {ipData?.asn?.route}</p>
                <p>Domain: {ipData?.asn?.domain}</p>
                <p>City: {ipData?.city}</p>
                <p>State: {ipData?.region}</p>
                <p>Country: {ipData?.country_name}</p>
                <p>Company name: {ipData?.asn?.name}</p>
            </div>
        </div>
    )
}