import VolumeGraph from "../components/VolumeGraph"
import PacketTypes from "../components/PacketTypes"
import TopDomains from "../components/TopDomains"

export default function Graphs() {
    return (
        <>
            <div className="volume-graph-container">
                <VolumeGraph />
            </div>
            <div className="graphs-container">
                <div className="graphs-container-item packet-types-chart">
                    <PacketTypes />
                </div>
                
                <div className="graphs-container-item">
                    <p className="top-domains-title">Most Visited Websites</p>
                    <TopDomains />
                </div>
            </div>
        </>
    )
}