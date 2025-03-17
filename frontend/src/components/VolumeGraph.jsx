import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, } from "recharts";

// Sample traffic data with timestamp, bytes_sent, and bytes_received
const data = [
    {
        timestamp: "12:00",    // Timestamp
        bytes_sent: 4000,      // Traffic data: bytes sent
        bytes_received: 2400,  // Traffic data: bytes received
    },
    {
        timestamp: "1:00",
        bytes_sent: 3000,
        bytes_received: 1500,
    },
    {
        timestamp: "2:00",
        bytes_sent: 2000,
        bytes_received: 1000,
    },
    {
        timestamp: "3:00",
        bytes_sent: 2780,
        bytes_received: 3908,
    },
    {
        timestamp: "4:00",
        bytes_sent: 1890,
        bytes_received: 4800,
    },
    {
        timestamp: "5:00",
        bytes_sent: 2390,
        bytes_received: 3800,
    },
    {
        timestamp: "6:00",
        bytes_sent: 3490,
        bytes_received: 4300,
    },
];

export default function VolumeGraph() {
    return (
        <AreaChart width={700} height={300} data={data}
            margin={{ top: 10, right: 30, left: 0, bottom: 0, }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="bytes_sent" stroke="#8884d8" fill="#8884d8" name="Bytes Sent" />
            <Area type="monotone" dataKey="bytes_received" stroke="#82ca9d" fill="#82ca9d" name="Bytes Received" />
        </AreaChart>
    )
}