import React, { useState, useEffect } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { 
  Activity, 
  TrendingUp, 
  Sparkles, 
  Award, 
  Sun, 
  Moon, 
  Cpu, 
  Menu, 
  X, 
  FileText, 
  ShieldCheck, 
  ArrowUpRight 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar({ theme, toggleTheme }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const mlTools = [
    {
      path: '/predict-salary',
      label: 'Salary Predictor',
      shortLabel: 'Salary',
      desc: 'HistGradientBoosting CTC Estimator',
      icon: <TrendingUp size={15} />
    },
    {
      path: '/resume-analyzer',
      label: 'Resume ATS 2.0',
      shortLabel: 'Resume ATS',
      desc: 'PDF Gap Analysis & Keyword Matcher',
      icon: <FileText size={15} />
    },
    {
      path: '/placement',
      label: 'Placement Readiness',
      shortLabel: 'Placement',
      desc: 'Logistic Regression Probability & Merit',
      icon: <Award size={15} />
    },
    {
      path: '/benchmarks',
      label: 'Model Benchmarks',
      shortLabel: 'Benchmarks',
      desc: 'Comparative Cross-Validation Evaluation',
      icon: <Cpu size={15} />
    }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-glassBorder bg-[#f8fafc]/95 dark:bg-[#070c14]/95 backdrop-blur-xl transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 group shrink-0">
          <div className="relative bg-gradient-to-br from-brandBlue/20 to-brandCyan/20 border border-brandBlue/30 p-2 rounded-xl flex items-center justify-center shadow-sm group-hover:border-brandBlue group-hover:shadow-[0_0_15px_rgba(14,165,233,0.3)] transition-all duration-300">
            <svg 
              className="w-5 h-5 text-brandBlue group-hover:scale-110 transition-transform duration-300" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id="nav-logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--color-primary)" />
                  <stop offset="100%" stopColor="var(--color-accent)" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="10" stroke="url(#nav-logo-grad)" strokeWidth="2" fill="none" className="opacity-95" />
              <path d="M12 2v2M12 20v2M2 12h2M20 12h2" stroke="url(#nav-logo-grad)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
              <circle cx="10.5" cy="10.5" r="4" stroke="currentColor" strokeWidth="2" fill="none" />
              <path d="M13.5 13.5L18.5 18.5" stroke="url(#nav-logo-grad)" strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="10.5" cy="10.5" r="1.5" fill="var(--color-accent)" />
            </svg>
          </div>
          
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-brandBlue via-brandCyan to-brandPurple bg-clip-text text-transparent">
              CareerLens
            </span>
            <span className="hidden xl:inline-flex px-1.5 py-0.5 text-[10px] font-bold rounded-md bg-brandBlue/10 text-brandBlue border border-brandBlue/20">
              AI 2.0
            </span>
          </div>
        </Link>

        {/* Structured Segmented Navigation Bar (Clean & Visible, No Overlapping Popups) */}
        <nav className="hidden md:flex items-center gap-1.5 p-1 rounded-2xl bg-brandSecondary/35 border border-glassBorder shadow-inner" aria-label="Main Navigation">
          
          {/* Pillar 1: Market */}
          <NavLink
            to="/"
            end
            className={({ isActive }) => 
              `flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                isActive 
                  ? 'bg-white dark:bg-[#0c1524] text-brandBlue shadow-sm border border-glassBorder' 
                  : 'text-textMuted hover:text-textMain hover:bg-brandSecondary/40'
              }`
            }
          >
            <Activity size={14} className="text-brandBlue" />
            <span>Market</span>
          </NavLink>

          {/* Predictive ML Tools Cluster */}
          <div className="flex items-center gap-1">
            {mlTools.map((tool) => (
              <NavLink
                key={tool.path}
                to={tool.path}
                className={({ isActive }) => 
                  `flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                    isActive 
                      ? 'bg-white dark:bg-[#0c1524] text-brandBlue shadow-sm border border-glassBorder' 
                      : 'text-textMuted hover:text-textMain hover:bg-brandSecondary/40'
                  }`
                }
              >
                {tool.icon}
                <span>{tool.shortLabel}</span>
              </NavLink>
            ))}
          </div>



        </nav>

        {/* Right Section: System Status & Theme Toggle */}
        <div className="flex items-center gap-2.5 shrink-0">
          
          {/* Live System Status */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-brandSecondary/50 border border-glassBorder text-xs text-textMain shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-medium text-textMuted text-[11px]">System</span>
            <span className="font-bold text-emerald-500 dark:text-emerald-400 text-[11px]">Live</span>
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded-xl border border-glassBorder bg-white/80 dark:bg-[#0c1524]/80 hover:bg-brandSecondary/60 flex items-center gap-1 transition-all duration-200 cursor-pointer shadow-sm"
            aria-label="Toggle Theme"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          >
            <div className={`p-1 rounded-lg transition-all duration-200 ${theme === 'light' ? 'bg-brandBlue text-white shadow-sm' : 'text-textMuted'}`}>
              <Sun size={15} />
            </div>
            <div className={`p-1 rounded-lg transition-all duration-200 ${theme === 'dark' ? 'bg-brandBlue text-white shadow-sm' : 'text-textMuted'}`}>
              <Moon size={15} />
            </div>
          </button>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-xl border border-glassBorder bg-white dark:bg-[#0c1524] text-textMain hover:bg-brandSecondary transition-colors cursor-pointer"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

        </div>

      </div>

      {/* Mobile Drawer Menu (Solid Background - 0% Bleed-through) */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-t border-glassBorder bg-white dark:bg-[#070c14] px-5 py-4 space-y-4 shadow-2xl"
          >
            {/* Core Links */}
            <div className="space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-textMuted px-2 mb-1">
                Market & Research
              </div>
              
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                  location.pathname === '/' ? 'bg-brandBlue/10 text-brandBlue font-semibold' : 'text-textMain hover:bg-brandSecondary/50'
                }`}
              >
                <Activity size={18} className="text-brandBlue" />
                <span>Market Insights</span>
              </Link>

            </div>

            {/* ML Tools Group */}
            <div className="space-y-1 border-t border-glassBorder pt-3">
              <div className="text-[10px] font-bold uppercase tracking-wider text-textMuted px-2 mb-1">
                Predictive ML Tools
              </div>
              {mlTools.map((tool) => (
                <Link
                  key={tool.path}
                  to={tool.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium ${
                    location.pathname === tool.path ? 'bg-brandBlue/10 text-brandBlue font-semibold' : 'text-textMain hover:bg-brandSecondary/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="text-brandBlue">{tool.icon}</div>
                    <span>{tool.label}</span>
                  </div>
                  <span className="text-[10px] text-textMuted">{tool.desc}</span>
                </Link>
              ))}
            </div>

            {/* System Status in Drawer */}
            <div className="flex items-center justify-between px-3 py-2.5 rounded-xl bg-brandSecondary/30 border border-glassBorder text-xs">
              <span className="text-textMuted">Backend System Status</span>
              <span className="inline-flex items-center gap-1.5 text-emerald-500 dark:text-emerald-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Connected & Ready
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </header>
  );
}
