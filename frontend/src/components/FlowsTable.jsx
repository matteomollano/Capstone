import { React, useMemo, useState, useEffect, useCallback, } from 'react';
import BaseTable from './common/BaseTable';

export default function FlowsTable() {

    const [flowData, setFlowData] = useState([]);
    
    useEffect(() => {
        // fetch data from flask backend via fetch
        fetch('http://localhost:5000/flowsTable')
            .then(response => response.json()) // parse JSON from the response
            .then(data => {
                setFlowData(data); // set the fetched data in state
            })
            .catch(error => {
                console.error('There was an error fetching the flow data.', error);
            });
    }, []);

    // function to open geolocation page in new tab when domain link is clicked
    const handleDomainClick = (ipData) => {
        // store the ipData in sessionStorage
        sessionStorage.setItem('ipData', JSON.stringify(ipData));

        // open the /geolocation page in a new tab
        window.open('/geolocation', '_blank');
    };

    // function to render IP or domain in FlowsTable
    const renderIpOrDomain = useCallback((ipData) => {

        const domain = ipData?.asn?.domain || ipData;      // use domain if available, else fallback to IP
        const isDomainAvailable = !!ipData?.asn?.domain;   // check if domain is available

        return (
            <span>
                {isDomainAvailable ? (
                    <button
                        onClick={() => handleDomainClick(ipData)}  // pass full ipData on click
                        style={{ 
                            color: 'lightblue', 
                            textDecoration: 'underline',
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            cursor: 'pointer',
                            font: 'inherit'
                        }} // make it look like a link
                    >
                        {domain}
                    </button>
                ) : (
                    domain  // display IP address if it doesn't have a domain name 
                            // (because it is a private IP)
                )}
            </span>
        );
    }, []);

    const flowColumns = useMemo(() => [
        {
            accessorKey: 'flow_id',
            header: 'Flow ID',
            size: 30,
        },
        {
            accessorKey: 'timestamp',
            header: 'Time',
            size: 75,
        },
        {
            accessorKey: 'src_ip',
            header: 'Source IP',
            size: 75,
            Cell: ({ cell }) => renderIpOrDomain(cell.getValue()),
        },
        {
            accessorKey: 'dst_ip',
            header: 'Dest IP',
            size: 75,
            Cell: ({ cell }) => renderIpOrDomain(cell.getValue()),
        },
        {
            accessorKey: 'src_port',
            header: 'Source Port',
            size: 75,
            Cell: ({ cell }) => cell.getValue() ?? 'N/A',
        },
        {
            accessorKey: 'dst_port',
            header: 'Dest Port',
            size: 75,
            Cell: ({ cell }) => cell.getValue() ?? 'N/A',
        },
        {
            accessorKey: 'protocol',
            header: 'Protocol',
            size: 75,
        },
        {
            accessorKey: 'num_packets',
            header: 'Packets',
            size: 75,
        },
        {
            accessorKey: 'bytes_src',
            header: 'Bytes Sent',
            size: 75,
        },
        {
            accessorKey: 'bytes_dst',
            header: 'Bytes Received',
            size: 75,
        },
        {
            accessorKey: 'is_malicious',
            header: 'Security Status',
            size: 75
        },
    ], [renderIpOrDomain]);

    return (
        <BaseTable
            data={flowData}
            columns={flowColumns}
        />
    )
}