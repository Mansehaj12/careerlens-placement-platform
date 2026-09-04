import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import MarketDashboard from './components/MarketDashboard';
import SalaryPredictor from './components/SalaryPredictor';
import ResumeMatcher from './components/ResumeMatcher';
import PlacementAnalytics from './components/PlacementAnalytics';
import ModelBenchmarks from './components/ModelBenchmarks';

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
      <div className="flex flex-col min-h-screen bg-darkBg text-textMain relative selection:bg-brandBlue/20 selection:text-brandBlue">
        
        {/* Atmospheric Ambient Lighting Glow */}
        <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[480px] pointer-events-none -z-10 overflow-hidden">
          <div className="absolute top-[-140px] left-1/2 -translate-x-1/2 w-[720px] h-[340px] bg-gradient-to-tr from-brandBlue/18 via-brandCyan/12 to-brandPurple/15 blur-[130px] rounded-full opacity-70 dark:opacity-45" />
          <div className="absolute top-[40px] right-[-100px] w-[360px] h-[280px] bg-brandCyan/10 blur-[110px] rounded-full opacity-60 dark:opacity-35" />
          <div className="absolute top-[80px] left-[-80px] w-[320px] h-[260px] bg-brandBlue/10 blur-[100px] rounded-full opacity-50 dark:opacity-30" />
        </div>

        {/* Navigation Bar */}
        <Navbar 
          theme={theme} 
          toggleTheme={toggleTheme} 
        />

        {/* Main Content Layout */}
        <main className="flex-1 w-full max-w-7xl mx-auto py-8 px-2 sm:px-4" id="app-main-content">
          <Routes>
            <Route path="/" element={<MarketDashboard />} />
            <Route path="/predict-salary" element={<SalaryPredictor />} />
            <Route path="/resume-analyzer" element={<ResumeMatcher />} />
            <Route path="/placement" element={<PlacementAnalytics />} />
            <Route path="/benchmarks" element={<ModelBenchmarks />} />
          </Routes>
        </main>

        {/* Global Footer */}
        <footer className="border-t border-glassBorder bg-darkBg/80 backdrop-blur-md py-6 text-xs text-textMuted w-full mt-auto">
          <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-tight bg-gradient-to-r from-brandBlue via-brandCyan to-brandPurple bg-clip-text text-transparent">
                CareerLens
              </span>
              <span>— Predictive Tech Placement & Salary Intelligence</span>
            </div>
            <p className="sm:text-right">
              Crafted by <span className="font-semibold text-textMain hover:text-brandBlue transition-colors duration-200">Mansehaj Preet Singh</span>
            </p>
          </div>
        </footer>

      </div>
    </BrowserRouter>
  );
}
