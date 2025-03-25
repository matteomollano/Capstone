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
                {/* <div className="graphs-container-item">
                    <VolumeGraph />
                </div>
                <div className="graphs-container-item">
                    <VolumeGraph />
                </div>              */}
                <div className="graphs-container-item">
                    <PacketTypes />
                </div>
                <div className="graphs-container-item">
                    <TopDomains />
                </div>
            </div>
        </>
    )
}