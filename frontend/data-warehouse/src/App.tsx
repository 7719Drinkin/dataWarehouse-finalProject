import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QueryDashboard from './pages/QueryDashboard';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<QueryDashboard />} />
        <Route path="/query" element={<QueryDashboard />} />
      </Routes>
    </Router>
  );
};

export default App;