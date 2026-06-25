import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import MarketDashboard from './components/MarketDashboard';
import SalaryPredictor from './components/SalaryPredictor';
import ResumeMatcher from './components/ResumeMatcher';
import PlacementAnalytics from './components/PlacementAnalytics';

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen bg-darkBg text-textMain">
        
        {/* Navigation Bar */}
        <Navbar theme={theme} toggleTheme={toggleTheme} />

        {/* Main Content Layout */}
        <main className="flex-1 w-full max-w-7xl mx-auto py-6" id="app-main-content">
          <Routes>
            <Route path="/" element={<MarketDashboard />} />
            <Route path="/predict-salary" element={<SalaryPredictor />} />
            <Route path="/resume-analyzer" element={<ResumeMatcher />} />
            <Route path="/placement" element={<PlacementAnalytics />} />
          </Routes>
        </main>

        {/* Global Footer */}
        <footer className="border-t border-glassBorder bg-darkBg/40 py-6 text-xs text-textMuted w-full">
          <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>© 2026 CareerLens. AI-Powered Job Market Intelligence Platform.</p>
            <p className="sm:text-right">
              Made by <span className="font-semibold text-textMain hover:text-brandBlue transition-colors duration-200">Mansehaj Preet Singh</span>
            </p>
          </div>
        </footer>

      </div>
    </BrowserRouter>
  );
}
