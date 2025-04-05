import React from 'react';
// for navigation with different routes
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from './pages/Layout';
import Home from './pages/Home';
import Tables from './pages/Tables';
import Graphs from './pages/Graphs';
import NoPage from './pages/NoPage';
import Geolocation from './pages/Geolocation';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="tables" element={<Tables />} />
          <Route path="graphs" element={<Graphs />} />
          <Route path="geolocation" element={<Geolocation />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}