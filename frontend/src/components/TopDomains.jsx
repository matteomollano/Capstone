import { useState, useEffect } from "react"

/* Wireframe data for testing */
// const data = [
//     { domain: "www.google.com", hits: 250, },
//     { domain: "www.amazon.com", hits: 200, },
//     { domain: "www.spotify.com", hits: 176, },
//     { domain: "my.hofstra.edu", hits: 143 },
//     { domain: "www.nike.com", hits: 50, },
// ]

// const totalHits = data.reduce((sum, item) => sum + item.hits, 0);

export default function TopDomains() {

    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:5000/topDomains')
            .then(response => response.json())
            .then(data => {
                setData(data);
            })
            .catch(error => {
                console.error('There was an error fetching the flow data.', error);
            });
    }, []);

    const totalHits = data.reduce((sum, item) => sum + item.hits, 0);

    return (
        <>
            <table className="top-domains-table">
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>Hits</th>
                        <th>Frequency</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, index) => (
                        <tr key={index}>
                            <td>{item.domain}</td>
                            <td>{item.hits}</td>
                            <td>{((item.hits / totalHits) * 100).toFixed(2)}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </>
    )
}