import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Activity, TrendingUp, Sparkles, Award, Sun, Moon } from 'lucide-react';

export default function Navbar({ theme, toggleTheme }) {
  const navItems = [
    { path: '/', label: 'Job Market Insights', icon: <Activity size={16} /> },
    { path: '/predict-salary', label: 'Salary Predictor', icon: <TrendingUp size={16} /> },
    { path: '/resume-analyzer', label: 'Resume Gap Analyzer', icon: <Sparkles size={16} /> },
    { path: '/placement', label: 'Placement Analytics', icon: <Award size={16} /> }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-glassBorder bg-darkBg/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="bg-darkCard border border-glassBorder p-2 rounded-xl flex items-center justify-center shadow-sm group-hover:border-brandBlue/50 transition-all duration-300">
            <svg 
              className="w-5 h-5 text-brandBlue" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--color-primary)" />
                  <stop offset="100%" stopColor="var(--color-accent)" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="10" stroke="url(#logo-grad)" strokeWidth="2" fill="none" className="opacity-95" />
              <path d="M12 2v2M12 20v2M2 12h2M20 12h2" stroke="url(#logo-grad)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
              <circle cx="10.5" cy="10.5" r="4" stroke="currentColor" strokeWidth="2" fill="none" />
              <path d="M13.5 13.5L18.5 18.5" stroke="url(#logo-grad)" strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="10.5" cy="10.5" r="1.5" fill="var(--color-accent)" />
            </svg>
          </div>
          <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-brandBlue via-brandCyan to-brandPurple bg-clip-text text-transparent">
            CareerLens
          </span>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive 
                    ? 'bg-brandBlue/10 text-brandBlue border border-brandBlue/20 shadow-sm' 
                    : 'text-textMuted hover:bg-brandSecondary hover:text-textMain'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Action Widgets / Theme Toggle */}
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-flex items-center gap-1.5 bg-brandSecondary border border-glassBorder text-xs text-brandSuccess font-semibold uppercase px-3 py-1 rounded-full">
            ● Live API Connected
          </span>
          <button
            onClick={toggleTheme}
            className="p-1 rounded-xl border border-glassBorder bg-darkCard flex items-center gap-1 transition-all duration-200 cursor-pointer shadow-sm"
            aria-label="Toggle Theme"
          >
            <div className={`p-1.5 rounded-lg transition-all duration-150 ${theme === 'light' ? 'bg-brandBlue text-white shadow-sm' : 'text-textMuted'}`}>
              <Sun size={14} />
            </div>
            <div className={`p-1.5 rounded-lg transition-all duration-150 ${theme === 'dark' ? 'bg-brandBlue text-white shadow-sm' : 'text-textMuted'}`}>
              <Moon size={14} />
            </div>
          </button>
        </div>

      </div>
    </header>
  );
}
