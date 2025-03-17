import { Chart } from "react-google-charts";

const data = [
    ["Protocol", "Number of packets"],
    ["HTTP", 500],
    ["TCP", 300],
    ["UDP", 360],
    ["ICMP", 200],
    ["SSH", 40],
];

const options = {
    title: "Packet Types Distribution",
    pieHole: 0.4,
    is3D: false,
    backgroundColor: "transparent",
    titleTextStyle: {
        color: "white",
    },
    legend: {
        textStyle: {
            color: "white",
        },
    },
    fontName: "Montserrat",
};

export default function PacketTypes() {
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