import VolumeGraph from "../components/VolumeGraph"
import PacketTypes from "../components/PacketTypes"
import TopDomains from "../components/TopDomains"

export default function Graphs() {
    return (
        <>
            <p>Graphs page here...</p>
            <div className="graphs-container">
                <VolumeGraph />
                <VolumeGraph />
                <PacketTypes />
                <TopDomains />
            </div>
        </>
    )
}