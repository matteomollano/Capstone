import { React, useMemo, useState, useEffect } from 'react';
import { MaterialReactTable, useMaterialReactTable } from 'material-react-table';

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
        },
        {
            accessorKey: 'dst_ip',
            header: 'Dest IP',
            size: 75,
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
    ], []);

    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
    const [sorting, setSorting] = useState([]);

    const table = useMaterialReactTable({
        columns: flowColumns,
        data: flowData, // data must be memoized or stable (useState, useMemo, defined outside of this component, etc.)
        enableDensityToggle: false, // disable density toggle
        enableFullScreenToggle: false, // disable full screen toggle
        initialState: { density: 'compact' },
        state: { pagination, sorting },
        onPaginationChange: setPagination,
        onSortingChange: setSorting,
    });

    return (
        <MaterialReactTable 
            table={table}
        />
    )
}