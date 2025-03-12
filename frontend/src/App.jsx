import React from 'react'
import Navbar from './components/Navbar';
import FlowsTable from './components/FlowsTable'
import { ThemeProvider, createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
    },
});

export default function App() {
  return (
    <>
      <Navbar />
      <div className='table-container'>
        <ThemeProvider theme={darkTheme}>
          <FlowsTable />
        </ThemeProvider>
      </div>
    </>
  )
}