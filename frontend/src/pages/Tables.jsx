import FlowsTable from "../components/FlowsTable";
import FramesTable from "../components/FramesTable";
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { useState, } from 'react';
import { Tabs, Tab, } from '@mui/material';

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
    },
});

export default function Table() {
    const [activeTab, setActiveTab] = useState(0);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    }

    return (
        <ThemeProvider theme={darkTheme}>
            {/* Tabs for switching between Flows and Frames tables */}
            <Tabs
                value={activeTab}
                onChange={handleTabChange}
                indicatorColor="primary"
                textColor="inherit"
                centered
                aria-label="Switch between Flows and Frames tables"
                sx={{
                    borderBottom: 1,
                    borderColor: 'divider',
                    '& .MuiTabs-indicator': {
                        backgroundColor: 'white',  // this makes the indicator white
                    },
                }}
            >
                <Tab label="Flows" sx={{ fontWeight: activeTab === 0 ? 'bold' : 'normal' }} />
                <Tab label="Frames" sx={{ fontWeight: activeTab === 1 ? 'bold' : 'normal' }} />
            </Tabs>

            {/* Conditionally render the active table */}
            {activeTab === 0 ? (
                <div className='table-container'>
                    {/* <p className="table-title">Flows</p> */}
                    <FlowsTable />
                </div>
            ) : (
                <div className='table-container'>
                    {/* <p className="table-title">Frames</p> */}
                    <FramesTable />
                </div>
            )}
        </ThemeProvider>
    )
}