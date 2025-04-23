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
    const handleLinkClick = async (ipAddress) => {
        // open Geolocation page with IP address as the URL parameter
        window.open(`/geolocation?ip=${ipAddress}`, '_blank');
    };

    // function to render IP or domain in FlowsTable
    const renderIpAddress = useCallback(({ cell, column, row }) => {

        const ipAddress = cell.getValue();
        const columnId =  column.id // get whether this is the 'src_ip' or 'dst_ip' column calling the function
        const isPublicIP = columnId === "src_ip" ? row.original.is_public_src_ip : row.original.is_public_dst_ip;

        return (
            <span>
                {isPublicIP ? (
                    <button
                        onClick={() => handleLinkClick(ipAddress)} // display public IP as a link
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
                        {ipAddress}
                    </button>
                ) : (
                    ipAddress // don't display as a link since it is a private IP
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
            Cell: renderIpAddress,
        },
        {
            accessorKey: 'dst_ip',
            header: 'Dest IP',
            size: 75,
            Cell: renderIpAddress,
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
    ], [renderIpAddress]);

    return (
        <BaseTable
            data={flowData}
            columns={flowColumns}
        />
    )
}