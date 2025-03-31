import { React, useState, useEffect, useMemo, } from 'react';
import BaseTable from './common/BaseTable';

export default function FramesTable() {

    const [frameData, setFrameData] = useState([]);
    
    useEffect(() => {
        // fetch data from flask backend via fetch
        fetch('http://localhost:5000/framesTable')
            .then(response => response.json()) // parse JSON from the response
            .then(data => {
                setFrameData(data); // set the fetched data in state
            })
            .catch(error => {
                console.error('There was an error fetching the flow data.', error);
            });
    }, []);

    const frameColumns = useMemo(() => [
        {
            accessorKey: 'frame_id',
            header: 'Frame ID',
            size: 15,
        },
        {
            accessorKey: 'flow_id',
            header: 'Flow ID',
            size: 15,
        },
        {
            accessorKey: 'src_mac',
            header: 'Source MAC',
            size: 50,
        },
        {
            accessorKey: 'dst_mac',
            header: 'Dest MAC',
            size: 50,
        },
        {
            accessorKey: 'ether_type',
            header: 'Ether Type',
            size: 50,
        },
        {
            accessorKey: 'protocol',
            header: 'Protocol',
            size: 50,
        },
    ], []);

    return (
        <BaseTable
            data={frameData}
            columns={frameColumns}
        />
    )
}