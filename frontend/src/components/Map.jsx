import { useEffect, useRef, } from 'react';
import mapboxgl from "mapbox-gl";
import 'mapbox-gl/dist/mapbox-gl.css';

// setting up access token
const mapboxToken = process.env.REACT_APP_MAPBOX_TOKEN
if (typeof mapboxToken === "undefined") {
    throw new Error("You need a mapbox token to run this application")
}
mapboxgl.accessToken = mapboxToken;

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

        map.current.on('style.load', () => {
            // set the light preset to be in dusk mode
            map.current.setConfigProperty('basemap', 'lightPreset', 'dusk');
        });

    }, [longitude, latitude]);

    return (
        <div className="map-component" ref={mapContainer} />
    )
}