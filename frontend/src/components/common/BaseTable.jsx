import { React, useState, } from 'react';
import { MaterialReactTable, useMaterialReactTable } from 'material-react-table';

export default function BaseTable({ data, columns, getRowStyle }) {
    
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
    const [sorting, setSorting] = useState([]);

    const table = useMaterialReactTable({
        columns: columns,
        data: data, // data must be memoized or stable (useState, useMemo, defined outside of this component, etc.)
        enableDensityToggle: false, // disable density toggle
        enableFullScreenToggle: false, // disable full screen toggle
        initialState: { density: 'compact' },
        state: { pagination, sorting },
        onPaginationChange: setPagination,
        onSortingChange: setSorting,
        muiTableBodyRowProps: ({ row }) => ({
            sx: getRowStyle ? getRowStyle(row) : {},
        }), // styling for each row in the table
    });

    return (
        <MaterialReactTable
            table={table}
        />
    );
}