import { useState } from 'react';

const featureDetails = {
    traffic: {
        title: "Traffic Analysis",
        image: "/traffic-analysis.webp",
        sections: [
            {
                subtitle: "Network Packet Capture",
                description: "Netara uses Python Scapy to sniff network packets from your local wifi network, providing real-time monitoring of your network traffic."
            },
            {
                subtitle: "Flow Analysis",
                description: "Packets from the same communication are categorized into network flows and stored in a database for comprehensive analysis."
            },
            {
                subtitle: "Machine Learning Detection",
                description: "Custom machine learning models analyze network flows to detect potential malicious activity and security threats."
            },
            {
                subtitle: "Data Visualization",
                description: "View all network data on the Tables page, with separate views for IP layer data (Flows table) and Ethernet layer data (Frames table)."
            }
        ]
    },
    visualizations: {
        title: "Visualizations",
        image: "/visualizations.png",
        sections: [
            {
                subtitle: "Interactive Charts",
                description: "Netara generates dynamic charts and graphs that update in real-time as new network data is captured."
            },
            {
                subtitle: "Traffic Patterns",
                description: "Visualize network traffic patterns and trends over time to identify unusual behavior."
            },
            {
                subtitle: "Security Insights",
                description: "Get visual alerts and indicators of potential security threats in your network."
            }
        ]
    },
    geolocation: {
        title: "Geolocation",
        image: "/geolocation.png",
        sections: [
            {
                subtitle: "Global Traffic Mapping",
                description: "View the geographical distribution of your network traffic on an interactive map created using Mapbox."
            },
            {
                subtitle: "Domain-based Information",
                description: "View IP information for a specific domain such as IP subnet, region and country, and company name."
            },
            {
                subtitle: "Location-based Analysis",
                description: "Identify suspicious traffic patterns based on geographical origin and destination."
            }
        ]
    }
};

export default function Home() {
    const [selectedFeature, setSelectedFeature] = useState("traffic");

    return (
        <div className="home-container">
            <section className="welcome-section">
                <h1>Welcome to Netara</h1>
                <p>A network monitoring solution that leverage Machine Learning to discover malicious traffic</p>
            </section>

            <section className="features-section">

                <div 
                    className={`feature-card ${selectedFeature === "traffic" ? "active": ""}`}
                    onClick={() => setSelectedFeature('traffic')}
                >
                    <h2>Traffic Analysis</h2>
                    <p>View detailed network flow and frame data</p>
                </div>

                <div
                    className={`feature-card ${selectedFeature === "visualizations" ? "active" : ""}`}
                    onClick={() => setSelectedFeature('visualizations')}
                >
                    <h2>Visualizations</h2>
                    <p>Interactive graphs and charts for network data</p>
                </div>

                <div
                    className={`feature-card ${selectedFeature === "geolocation" ? "active" : ""}`}
                    onClick={() => setSelectedFeature('geolocation')}
                >
                    <h2>Geolocation</h2>
                    <p>Real-time maps of your network's global reach</p>
                </div>

            </section>

            {selectedFeature && (
                <section className="feature-detail-section">
                    <div className="feature-detail-container">
                        <div className="feature-image">
                            <img
                                src={featureDetails[selectedFeature].image}
                                alt={featureDetails[selectedFeature].title}
                            />
                        </div>
                        <div className="feature-description">
                            <h2>{featureDetails[selectedFeature].title}</h2>
                            {featureDetails[selectedFeature].sections.map((section, index) => (
                                <div key={index} className="feature-section">
                                    <h4>{section.subtitle}</h4>
                                    <p>{section.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            )}

        </div>
    )
}