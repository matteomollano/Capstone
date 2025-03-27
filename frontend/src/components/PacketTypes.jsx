import { useState, useEffect } from "react";
import { Chart } from "react-google-charts";

/* Wireframe data for testing */
// const data = [
//     ["Protocol", "Number of packets"],
//     ["HTTP", 500],
//     ["TCP", 300],
//     ["UDP", 360],
//     ["ICMP", 200],
//     ["SSH", 40],
// ];

export default function PacketTypes() {

    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:5000/packetTypes')
            .then(response => response.json())
            .then(data => {
                setData(data);
            })
            .catch(error => {
                console.error('There was an error fetching the flow data.', error);
            });
    }, []);

    const options = {
        title: "Packet Types Distribution",
        pieHole: 0.4,
        is3D: false,
        backgroundColor: "transparent",
        titleTextStyle: {
            color: "white",
            fontSize: 21,
        },
        legend: {
            textStyle: {
                color: "white",
            },
        },
        fontName: "Montserrat",
    };

    return (
        <Chart
            chartType="PieChart"
            width="100%"
            height="400px"
            data={data}
            options={options}
        />
    );
}