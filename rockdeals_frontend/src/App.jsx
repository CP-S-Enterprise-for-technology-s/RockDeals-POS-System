import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Reports from './components/Reports';
import Products from './components/Products';
import Customers from './components/Customers';
import POS from './components/POS';
import './App.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [currentUser] = useState({
    name: 'Alexandra Alex',
    role: 'Admin Store',
    avatar: '/api/placeholder/40/40'
  });

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('light');
  };

  return (
    <Router>
      <div className={`min-h-screen ${isDarkMode ? 'dark' : 'light'}`}>
        <div className="flex h-screen bg-background">
          {/* Sidebar */}
          <Sidebar />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header 
              user={currentUser} 
              isDarkMode={isDarkMode} 
              onToggleTheme={toggleTheme} 
            />
            
            {/* Page Content */}
            <main className="flex-1 overflow-x-hidden overflow-y-auto bg-background p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/products" element={<Products />} />
                <Route path="/customers" element={<Customers />} />
                <Route path="/pos" element={<POS />} />
              </Routes>
            </main>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;

