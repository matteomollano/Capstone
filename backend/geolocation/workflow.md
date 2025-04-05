## Part 1 - Update JSON response in Flask backend
Update get_flow_table in query_apis.py to return json as:

```json
flow = {
    "flow_id": row[0],
    "timestamp": str(row[1]),
    "src_ip": row[2],
    "dst_ip": {
        "ip": "142.250.65.238",
        "city": null,
        "region": null,
        "country_name": "United States",
        "continent_name": "North America",
        "latitude": 37.750999450683594,
        "longitude": -97.8219985961914,
        "flag": "https://ipdata.co/flags/us.png",
        "asn": {
            "asn": "AS15169",
            "name": "Google LLC",
            "domain": "google.com",
            "route": "142.250.65.0/24",
            "type": "business"
        }
    },
    "src_port": row[4],
    "dst_port": row[5],
    "protocol": row[6],
    "num_packets": row[7],
    "bytes_src": row[8],
    "bytes_dst": row[9],
    "is_malicious": row[10]
}
```

src_ip and dst_ip will be checked for public ip. If it is a public ip, then an ipdata api request will be made to get more detailed information.

<br>

## Part 2 - Update FlowsTable to show domain links for public IPs
In the frontend for FlowsTable, I will make all public ips display their domain name using dst_ip.asn.domain.
I will also make the domain names clickable and lightblue in color.

I will use a common function to work for both src and dst:
```javascript
// common logic to render IP or domain
const renderIpOrDomain = (ipData) => {
    const domain = ipData?.asn?.domain || ipData;     // use domain if available, else fallback to IP
    const isDomainAvailable = !!ipData?.asn?.domain;  // check if domain is available

    return (
        <span>
            {isDomainAvailable ? (
                <button
                    onClick={() => handleDomainClick(ipData)}  // pass full ipData on click
                    style={{ 
                        color: 'lightblue', 
                        textDecoration: 'underline',
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer',
                        font: 'inherit'
                    }} // make it look like a link
                >
                    {domain}
                </button>
            ) : (
                domain  // display IP address if it doesn't have a domain name 
                        // (because it is a private IP)
            )}
        </span>
    );
};
```

Then just need this in column accessors:
```javascript
{
    accessorKey: 'src_ip',
    header: 'Source IP',
    size: 75,
    // Modify the rendering of the src_ip column
    Cell: ({ cell }) => renderIpOrDomain(cell.getValue()),  // Use the common function
},
{
    accessorKey: 'dst_ip',
    header: 'Dest IP',
    size: 75,
    // Modify the rendering of the dst_ip column
    Cell: ({ cell }) => renderIpOrDomain(cell.getValue()),  // Use the common function
},
```

<br>

## Part 3 - Send data to Geolocation component
There are two ways to do this.

### Option 1

First way, use navigate and location (will open the /geolocation route in the same tab).
To accomplish this, put the following code in FlowsTable:
```javascript
import { useNavigate } from 'react-router-dom';

export default function FlowsTable() {
    const navigate = useNavigate();  // use the navigate function

    const handleDomainClick = (ipData) => {
        // navigate to the /geolocation page and pass the full ipData
        navigate('/geolocation', { state: { ipData } });
    };
    // ...
}
```
Then we need to use this passed data inside of the Geolocation component.
Inside of Geolocation, add this:
```javascript
import { useLocation } from 'react-router-dom'; 

export default function Geolocation() {
    // using navigator and location to access state (keeps within same tab)
    const { state } = useLocation();  // access the state passed from FlowsTable
    const ipData = state?.ipData;     // extract the ipData from the state
    
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
```

### Option 2

The second way to accomplish this is to use session storage. This will allow us to open the /geolocation route in a new tab.
To accomplish this, put the following code in FlowsTable:
```javascript
export default function FlowsTable() {
    // function to open geolocation page in new tab when domain link is clicked
    const handleDomainClick = (ipData) => {
        // store the ipData in sessionStorage
        sessionStorage.setItem('ipData', JSON.stringify(ipData));

        // open the /geolocation page in a new tab
        window.open('/geolocation', '_blank');
    };
    // ...
}
```
Then we need to use this passed data inside of the Geolocation component.
Inside of Geolocation, add this:
```javascript
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
```

<br>

## Part 4 - Use the coordinates inside of the Map component
```javascript
export default function Map({ latitude, longitude }) {
    // references to map container and the actual map
    const mapContainer = useRef(null);
    const map = useRef(null);

    useEffect(() => {
        if (!map.current && mapContainer.current) {
            map.current = new mapboxgl.Map({
                container: mapContainer.current,
                attributionControl: true,
                center: [longitude, latitude],
                zoom: 11.5,
                pitch: 50,
                bearing: -45,
                style: 'mapbox://styles/mapbox/standard',
            });
        }

        // update the map center whenever latitude or longitude changes
        if (map.current) {
            map.current.setCenter([longitude, latitude]);
        }

        map.current.on('style.load', () => {
            // set the light preset to be in dusk mode
            map.current.setConfigProperty('basemap', 'lightPreset', 'dusk');
        });

        // cleanup on unmount to prevent memory leaks
        return () => {
            if (map.current) {
                map.current.remove();
            }
        };

    }, [latitude, longitude]); // re-run the effect when latitude or longitude changes

    return (
        <div className="map-component" ref={mapContainer} />
    );
}
```