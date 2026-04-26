import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DemoCollection from './pages/DemoCollection';
import DemoPDP from './pages/DemoPDP';
import AdminLogin from './pages/AdminLogin';
import AdminProducts from './pages/AdminProducts';
import AdminProductDetail from './pages/AdminProductDetail';
import AdminFunnel from './pages/AdminFunnel';
import AdminSegments from './pages/AdminSegments';
import AdminPrivacy from './pages/AdminPrivacy';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/demo/collection" replace />} />
        <Route path="/demo/collection" element={<DemoCollection />} />
        <Route path="/demo/pdp/:productHandle" element={<DemoPDP />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<Navigate to="/admin/products" replace />} />
        <Route path="/admin/products" element={<AdminProducts />} />
        <Route path="/admin/products/:productId" element={<AdminProductDetail />} />
        <Route path="/admin/funnel" element={<AdminFunnel />} />
        <Route path="/admin/segments" element={<AdminSegments />} />
        <Route path="/admin/privacy" element={<AdminPrivacy />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
