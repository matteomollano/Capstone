import { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, } from "recharts";

// Sample traffic data with timestamp, bytes_sent, and bytes_received
// const data = [
//     {
//         time_interval: "12:00",    // Timestamp
//         bytes_sent: 4000,      // Traffic data: bytes sent
//         bytes_received: 2400,  // Traffic data: bytes received
//     },
//     {
//         time_interval: "1:00",
//         bytes_sent: 3000,
//         bytes_received: 1500,
//     },
//     {
//         time_interval: "2:00",
//         bytes_sent: 2000,
//         bytes_received: 1000,
//     },
//     {
//         time_interval: "3:00",
//         bytes_sent: 2780,
//         bytes_received: 3908,
//     },
//     {
//         time_interval: "4:00",
//         bytes_sent: 1890,
//         bytes_received: 4800,
//     },
//     {
//         time_interval: "5:00",
//         bytes_sent: 2390,
//         bytes_received: 3800,
//     },
//     {
//         time_interval: "6:00",
//         bytes_sent: 3490,
//         bytes_received: 4300,
//     },
// ];

export default function VolumeGraph() {

    const [data, setData] = useState([]);

    useEffect(() => {
            fetch('http://localhost:5000/volumeData')
                .then(response => response.json())
                .then(data => {
                    setData(data);
                })
                .catch(error => {
                    console.error('There was an error fetching the flow data.', error);
                });
        }, []);

    return (
        <ResponsiveContainer width="95%" height={300}>
            <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time_interval" interval="preserveStartEnd" />
                <YAxis tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} />
                <Tooltip />
                <Area type="monotone" dataKey="bytes_sent" stackId="1" stroke="#8884d8" fill="#8884d8" name="Bytes Sent"/>
                <Area type="monotone" dataKey="bytes_received" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Bytes Received" />
            </AreaChart>
        </ResponsiveContainer> 
    )
}