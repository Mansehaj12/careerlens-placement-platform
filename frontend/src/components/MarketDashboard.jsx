import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { 
  Briefcase, IndianRupee, MapPin, Activity, Search, Sparkles, Globe, ShieldCheck, Database, Layers
} from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../config';

export default function MarketDashboard() {
  const [data, setData] = useState(null);
  const [quality, setQuality] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState('Software Engineer');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('analytics'); // analytics vs pipeline
  const [currentPage, setCurrentPage] = useState(1);

  // Monitor theme switching dynamically to adapt chart colors
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/market/stats`)
      .then((res) => {
        if (!res.ok) throw new Error('API offline');
        return res.json();
      })
      .then((resData) => {
        setData(resData.dashboard);
        setQuality(resData.quality);
        setLoading(false);
      })
      .catch((err) => {
        console.warn("Flask server offline, loading static fallbacks...");
        // Load fallback files in public/data directly if server is not running
        Promise.all([
          fetch('/data/dashboard_data.json').then(r => r.json()),
          fetch('/data/data_quality.json').then(r => r.json())
        ]).then(([dData, qData]) => {
          setData(dData);
          setQuality(qData);
          setLoading(false);
        }).catch(fallbackErr => {
          console.error("Critical: Could not load analytical data.", fallbackErr);
        });
      });
  }, []);

  if (loading || !data) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <div className="h-10 w-64 skeleton animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="h-32 skeleton animate-pulse" />
          <div className="h-32 skeleton animate-pulse" />
          <div className="h-32 skeleton animate-pulse" />
          <div className="h-32 skeleton animate-pulse" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-80 skeleton animate-pulse" />
          <div className="h-80 skeleton animate-pulse" />
        </div>
      </div>
    );
  }

  // Pre-filter job postings sample
  const filteredJobs = data.sample_jobs.filter(job => {
    return (
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.clean_location.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.clean_skills_str.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const itemsPerPage = 8;
  const totalPages = Math.ceil(filteredJobs.length / itemsPerPage);
  const activePage = Math.min(currentPage, Math.max(1, totalPages));
  const startIndex = (activePage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, filteredJobs.length);
  const paginatedJobs = filteredJobs.slice(startIndex, endIndex);

  // Curated human-made colors
  const indigoColor = isDark ? '#6366f1' : '#4f46e5';
  const tealColor = isDark ? '#2dd4bf' : '#0f766e';
  const purpleColor = isDark ? '#a78bfa' : '#7c3aed';
  const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(9,9,11,0.05)';
  const textColor = isDark ? '#a1a1aa' : '#71717a';
  const tooltipBg = isDark ? '#121215' : '#ffffff';
  const tooltipBorder = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(9,9,11,0.08)';

  const COLORS = [
    indigoColor, 
    tealColor, 
    purpleColor, 
    isDark ? '#34d399' : '#059669', 
    isDark ? '#fbbf24' : '#d97706', 
    isDark ? '#f87171' : '#dc2626', 
    isDark ? '#f472b6' : '#db2777', 
    isDark ? '#818cf8' : '#4f46e5'
  ];
  
  const formatFullINR = (usdVal) => {
    if (usdVal === undefined || usdVal === null) return '₹0';
    const inrVal = usdVal * 83.333;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(inrVal);
  };

  const formatCompactINR = (usdVal) => {
    if (usdVal === undefined || usdVal === null) return '₹0';
    const inrVal = usdVal * 83.333;
    if (inrVal >= 10000000) {
      return `₹${(inrVal / 10000000).toFixed(2)} Cr`;
    } else if (inrVal >= 100000) {
      return `₹${(inrVal / 100000).toFixed(1)}L`;
    } else if (inrVal >= 1000) {
      return `₹${(inrVal / 1000).toFixed(0)}k`;
    }
    return `₹${inrVal.toFixed(0)}`;
  };

  // Custom tooltips for charting aesthetics
  const renderTooltip = (active, payload, label, isSalary = true, suffix = '') => {
    if (active && payload && payload.length) {
      const val = payload[0].value;
      const formattedVal = isSalary ? formatFullINR(val) : val.toLocaleString() + suffix;
      return (
        <div 
          className="rounded-xl p-3 shadow-lg border text-left"
          style={{ backgroundColor: tooltipBg, borderColor: tooltipBorder }}
        >
          <p className="text-[10px] font-bold text-textMuted uppercase tracking-wider mb-1">{label}</p>
          <p className="text-sm font-bold text-textMain">
            {formattedVal}
          </p>
        </div>
      );
    }
    return null;
  };

  const getPageNumbers = () => {
    const pages = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);
      
      let start = Math.max(2, activePage - 1);
      let end = Math.min(totalPages - 1, activePage + 1);
      
      if (activePage <= 3) {
        end = 4;
      } else if (activePage >= totalPages - 2) {
        start = totalPages - 3;
      }
      
      if (start > 2) {
        pages.push('ellipsis-start');
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      if (end < totalPages - 1) {
        pages.push('ellipsis-end');
      }
      
      pages.push(totalPages);
    }
    return pages;
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      
      {/* Title Header */}
      <motion.div 
        initial={{ opacity: 0, y: -5 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8"
      >
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-textMain font-sans">Job Market Insights</h1>
          <p className="text-textMuted text-sm mt-1.5 font-normal">
            Real-time trends and salary indicators parsed from over <strong className="text-brandBlue font-semibold">{data.totals.total_jobs.toLocaleString()}</strong> active listings.
          </p>
        </div>

        {/* Tab Selection */}
        <div className="flex bg-brandSecondary p-1 border border-glassBorder rounded-xl self-start md:self-auto shadow-inner">
          <button 
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 text-xs font-bold rounded-lg uppercase tracking-wider transition-all duration-200 cursor-pointer ${activeTab === 'analytics' ? 'bg-brandBlue text-white shadow' : 'text-textMuted hover:text-textMain'}`}
            id="tab-analytics"
          >
            <div className="flex items-center gap-1.5">
              <Activity size={14} /> Analytics Dashboard
            </div>
          </button>
          <button 
            onClick={() => setActiveTab('pipeline')}
            className={`px-4 py-2 text-xs font-bold rounded-lg uppercase tracking-wider transition-all duration-200 cursor-pointer ${activeTab === 'pipeline' ? 'bg-brandBlue text-white shadow' : 'text-textMuted hover:text-textMain'}`}
            id="tab-pipeline-quality"
          >
            <div className="flex items-center gap-1.5">
              <Database size={14} /> Data Quality Report
            </div>
          </button>
        </div>
      </motion.div>

      {activeTab === 'analytics' ? (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="space-y-8"
        >
          {/* KPI Metrics Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-card relative overflow-hidden p-6 flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-[3px] bg-brandBlue" />
              <div className="flex justify-between items-start text-textMuted mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Total Tech Postings</span>
                <div className="bg-brandBlue/10 p-2 rounded-xl text-brandBlue"><Briefcase size={16} /></div>
              </div>
              <h3 className="text-2xl font-extrabold text-textMain mt-1">{data.totals.total_jobs.toLocaleString()}</h3>
              <span className="text-xs text-brandSuccess font-medium mt-2 flex items-center gap-1">✓ Active Job Aggregation</span>
            </div>

            <div className="glass-card relative overflow-hidden p-6 flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-[3px] bg-brandPurple" />
              <div className="flex justify-between items-start text-textMuted mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Avg Base Salary</span>
                <div className="bg-brandPurple/10 p-2 rounded-xl text-brandPurple"><IndianRupee size={16} /></div>
              </div>
              <h3 className="text-2xl font-extrabold text-textMain mt-1">{formatFullINR(data.totals.global_avg_salary)}</h3>
              <span className="text-xs text-brandSuccess font-medium mt-2 flex items-center gap-1">✓ Indian Market Benchmark</span>
            </div>

            <div className="glass-card relative overflow-hidden p-6 flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-[3px] bg-brandCyan" />
              <div className="flex justify-between items-start text-textMuted mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Remote Ratio</span>
                <div className="bg-brandCyan/10 p-2 rounded-xl text-brandCyan"><Globe size={16} /></div>
              </div>
              <h3 className="text-2xl font-extrabold text-textMain mt-1">{data.totals.remote_ratio.toFixed(1)}%</h3>
              <span className="text-xs text-brandCyan font-medium mt-2">Remote-first Opportunities</span>
            </div>

            <div className="glass-card relative overflow-hidden p-6 flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-[3px] bg-brandSuccess" />
              <div className="flex justify-between items-start text-textMuted mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Demand Highlight</span>
                <div className="bg-brandSuccess/10 p-2 rounded-xl text-brandSuccess"><Sparkles size={16} /></div>
              </div>
              <h3 className="text-2xl font-extrabold text-textMain mt-1">{data.top_skills[0]?.skill || 'SQL'}</h3>
              <span className="text-xs text-textMuted mt-2">Required in {Math.round((data.top_skills[0]?.count / data.totals.total_jobs) * 100)}% of specs</span>
            </div>
          </div>

          {/* Primary Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Average Salaries by Role */}
            <div className="glass-card p-6">
              <h3 className="text-sm font-bold text-textMain mb-6 flex items-center gap-2">
                <IndianRupee size={16} className="text-brandBlue" /> Average Annual Salary by Role Profile
              </h3>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.role_stats} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="chartSalaryGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={indigoColor} stopOpacity={0.15}/>
                        <stop offset="95%" stopColor={indigoColor} stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis dataKey="standard_title" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} interval={0} angle={-15} textAnchor="end" height={45} />
                    <YAxis stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} tickFormatter={formatCompactINR} />
                    <Tooltip content={({ active, payload, label }) => renderTooltip(active, payload, label, true)} />
                    <Area type="monotone" dataKey="avg_salary" stroke={indigoColor} strokeWidth={2} fillOpacity={1} fill="url(#chartSalaryGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Dynamic Skills Bar Chart */}
            <div className="glass-card p-6">
              <div className="flex justify-between items-center mb-6 flex-wrap gap-2">
                <h3 className="text-sm font-bold text-textMain flex items-center gap-2">
                  <Sparkles size={16} className="text-brandCyan" /> Technology Demands by Role
                </h3>
                <select 
                  className="bg-brandSecondary border border-glassBorder rounded-lg px-2.5 py-1 text-xs text-textMain outline-none focus:border-brandBlue cursor-pointer"
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  id="role-filter-skills"
                >
                  {data.role_stats.map(r => (
                    <option key={r.standard_title} value={r.standard_title}>{r.standard_title}</option>
                  ))}
                </select>
              </div>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.skills_by_role[selectedRole] || []} layout="vertical" margin={{ top: 5, right: 10, left: 15, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis type="number" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} />
                    <YAxis type="category" dataKey="skill" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} />
                    <Tooltip content={({ active, payload, label }) => renderTooltip(active, payload, label, false, ' listings')} />
                    <Bar dataKey="count" fill={tealColor} radius={[0, 4, 4, 0]} maxBarSize={16}>
                      {(data.skills_by_role[selectedRole] || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* Secondary Charts */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Remote Donut */}
            <div className="glass-card p-6 flex flex-col justify-between">
              <h3 className="text-sm font-bold text-textMain mb-4">Workplace Format</h3>
              <div className="flex items-center justify-center h-48">
                <div className="h-full w-1/2 min-w-[100px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={data.remote_stats}
                        cx="50%"
                        cy="50%"
                        innerRadius={36}
                        outerRadius={54}
                        paddingAngle={4}
                        dataKey="count"
                      >
                        {data.remote_stats.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={index === 0 ? textColor : tealColor} />
                        ))}
                      </Pie>
                      <Tooltip content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div 
                              className="rounded-xl p-2 shadow-md border text-xs" 
                              style={{ backgroundColor: tooltipBg, borderColor: tooltipBorder }}
                            >
                              <span className="text-textMuted uppercase font-bold tracking-wider">{payload[0].payload.clean_remote === 'Yes' ? 'Remote' : 'On-Site'}:</span>
                              <span className="text-textMain font-semibold ml-1">{payload[0].value.toLocaleString()} jobs</span>
                            </div>
                          );
                        }
                        return null;
                      }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3 w-1/2 pl-2">
                  {data.remote_stats.map((item, idx) => (
                    <div key={item.clean_remote} className="text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-textMain">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ background: idx === 0 ? textColor : tealColor }} />
                        <span>{item.clean_remote === 'Yes' ? 'Remote' : 'On-Site'}</span>
                      </div>
                      <span className="text-textMuted block ml-4 text-[10px]">Avg: {formatCompactINR(item.avg_salary)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Experience Level Distribution */}
            <div className="glass-card p-6">
              <h3 className="text-sm font-bold text-textMain mb-6">Salary by Experience Tier</h3>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.experience_stats} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis dataKey="clean_experience" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} />
                    <YAxis stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} tickFormatter={formatCompactINR} />
                    <Tooltip content={({ active, payload, label }) => renderTooltip(active, payload, label, true)} />
                    <Bar dataKey="avg_salary" fill={purpleColor} radius={[4, 4, 0, 0]} maxBarSize={18} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Geography hubs */}
            <div className="glass-card p-6">
              <h3 className="text-sm font-bold text-textMain mb-6">Hub Availability (Postings)</h3>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.location_stats.sort((a,b)=>b.count-a.count).slice(0, 5)} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis dataKey="clean_location" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} />
                    <YAxis stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} />
                    <Tooltip content={({ active, payload, label }) => renderTooltip(active, payload, label, false, ' postings')} />
                    <Bar dataKey="count" fill={indigoColor} radius={[4, 4, 0, 0]} maxBarSize={18} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* Interactive Job Explorer List */}
          <div className="glass-card p-6">
            <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
              <div>
                <h3 className="text-base font-bold text-textMain">Market Listings Explorer</h3>
                <p className="text-textMuted text-xs mt-1">Browse cleaned production-grade listings indexed in our platform.</p>
              </div>
              <div className="flex items-center bg-brandSecondary border border-glassBorder rounded-xl px-3 py-2 w-72 focus-within:border-brandBlue transition-all duration-200">
                <Search size={16} className="text-textMuted mr-2" />
                <input 
                  type="text" 
                  placeholder="Search titles, companies, skills..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-transparent border-none outline-none text-xs text-textMain w-full"
                  id="explorer-search"
                />
              </div>
            </div>

            <div className="overflow-x-auto border border-glassBorder rounded-xl">
              <table className="w-full border-collapse text-left text-xs min-w-[700px]">
                <thead>
                  <tr className="border-b border-glassBorder bg-brandSecondary">
                    <th className="p-4 text-textMuted font-bold uppercase tracking-wider">Company</th>
                    <th className="p-4 text-textMuted font-bold uppercase tracking-wider">Role Profile</th>
                    <th className="p-4 text-textMuted font-bold uppercase tracking-wider">Location & Type</th>
                    <th className="p-4 text-textMuted font-bold uppercase tracking-wider">Experience</th>
                    <th className="p-4 text-textMuted font-bold uppercase tracking-wider">Salary Range</th>
                    <th className="p-4 text-textMuted font-bold uppercase tracking-wider">Key Technologies</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedJobs.map((job, idx) => (
                    <tr key={idx} className="border-b border-glassBorder hover:bg-brandSecondary/50 transition-colors">
                      <td className="p-4 font-semibold text-textMain">{job.company}</td>
                      <td className="p-4 text-textMain">{job.standard_title}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-1.5">
                          <span className="inline-flex items-center gap-1 text-textMuted"><MapPin size={12} />{job.clean_location}</span>
                          {job.clean_remote === 'Yes' ? (
                            <span className="bg-brandCyan/10 text-brandCyan text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded border border-brandCyan/15">Remote</span>
                          ) : (
                            <span className="bg-brandWarning/10 text-brandWarning text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded border border-brandWarning/15">Office</span>
                          )}
                        </div>
                      </td>
                      <td className="p-4 capitalize text-textMuted">{job.clean_experience}</td>
                      <td className="p-4 font-semibold text-brandSuccess">{formatCompactINR(job.salary_min)} - {formatCompactINR(job.salary_max)}</td>
                      <td className="p-4 max-w-[220px] truncate">
                        <div className="flex flex-wrap gap-1">
                          {job.clean_skills_str.split(',').slice(0, 3).map((s, sIdx) => (
                            <span key={sIdx} className="bg-brandBlue/10 text-brandBlue text-[9px] font-semibold px-1.5 py-0.5 rounded">
                              {s.trim ? s.trim() : s}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filteredJobs.length === 0 && (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-textMuted">No postings matched your criteria.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6 pt-4 border-t border-glassBorder text-xs">
                <div className="text-textMuted font-medium">
                  Showing <span className="text-textMain font-bold">{startIndex + 1}</span> to <span className="text-textMain font-bold">{endIndex}</span> of <span className="text-textMain font-bold">{filteredJobs.length}</span> postings
                </div>
                
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={activePage === 1}
                    className="px-3 py-1.5 rounded-lg border border-glassBorder bg-darkCard text-textMuted hover:text-textMain hover:border-brandBlue/50 disabled:opacity-30 disabled:pointer-events-none transition-all duration-150 cursor-pointer"
                  >
                    Prev
                  </button>
                  
                  {getPageNumbers().map((page, index) => {
                    if (page === 'ellipsis-start' || page === 'ellipsis-end') {
                      return (
                        <span key={`ellipsis-${index}`} className="text-textMuted px-1.5 select-none font-bold">
                          ...
                        </span>
                      );
                    }
                    return (
                      <button
                        type="button"
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`w-8 h-8 rounded-lg border flex items-center justify-center font-bold transition-all duration-150 cursor-pointer ${
                          activePage === page
                            ? 'bg-brandBlue border-brandBlue text-white shadow'
                            : 'border-glassBorder bg-darkCard text-textMuted hover:text-textMain hover:border-brandBlue/50'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                  
                  <button
                    type="button"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={activePage === totalPages}
                    className="px-3 py-1.5 rounded-lg border border-glassBorder bg-darkCard text-textMuted hover:text-textMain hover:border-brandBlue/50 disabled:opacity-30 disabled:pointer-events-none transition-all duration-150 cursor-pointer"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      ) : (
        /* Data quality report tab */
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="space-y-8"
        >
          {/* Data Quality Report Card */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-6">
              <ShieldCheck size={20} className="text-brandSuccess" />
              <h3 className="text-base font-bold text-textMain">ETL Pipeline Quality Evaluation</h3>
            </div>
            
            <p className="text-textMuted text-xs mb-8 leading-relaxed max-w-3xl">
              We parsed and cleaned incoming developer job listings before statistical fitting. Below is an audit detailing values imputed, dropped, and standardized.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              {/* Raw Messy Data Metrics */}
              <div className="bg-brandSecondary/50 border border-glassBorder rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4 text-brandDanger">
                  <Layers size={18} />
                  <h4 className="font-bold text-xs uppercase tracking-wider">Raw Ingested Data</h4>
                </div>
                <ul className="space-y-4 text-xs">
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Total Records Ingested</span>
                    <span className="font-bold text-textMain">{quality?.before.total_records.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Inconsistent/Missing Salary Bands</span>
                    <span className="font-bold text-brandDanger">{quality?.before.missing_salaries.toLocaleString()} rows</span>
                  </li>
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Missing Geographical Metadata</span>
                    <span className="font-bold text-brandDanger">{quality?.before.missing_locations.toLocaleString()} rows</span>
                  </li>
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Missing Experience Level</span>
                    <span className="font-bold text-brandDanger">{quality?.before.missing_experience.toLocaleString()} rows</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-textMuted">Duplicate Listings Identified</span>
                    <span className="font-bold text-brandDanger">{quality?.before.duplicate_records.toLocaleString()} rows</span>
                  </li>
                </ul>
              </div>

              {/* Cleaned Standardized Metrics */}
              <div className="bg-brandSecondary/50 border border-brandSuccess/20 rounded-2xl p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4 text-brandSuccess">
                  <ShieldCheck size={18} />
                  <h4 className="font-bold text-xs uppercase tracking-wider">Standardized Store (Production)</h4>
                </div>
                <ul className="space-y-4 text-xs">
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Cleaned Table Records</span>
                    <span className="font-bold text-textMain">{quality?.after.total_records.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Missing Salary Bands (Imputed)</span>
                    <span className="font-bold text-brandSuccess">0 rows (100% clean)</span>
                  </li>
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Missing Locations (Resolved)</span>
                    <span className="font-bold text-brandSuccess">0 rows (100% clean)</span>
                  </li>
                  <li className="flex justify-between border-b border-glassBorder pb-2">
                    <span className="text-textMuted">Missing Experience Level (Standardized)</span>
                    <span className="font-bold text-brandSuccess">0 rows (100% clean)</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-textMuted">Duplicates Dropped</span>
                    <span className="font-bold text-brandSuccess">{quality?.before.duplicate_records.toLocaleString()} rows</span>
                  </li>
                </ul>
              </div>

            </div>

            {/* Outliers summary box */}
            <div className="mt-8 bg-brandSecondary/40 border border-glassBorder rounded-xl p-5 text-xs flex gap-4 items-start">
              <Database size={20} className="text-brandCyan mt-0.5 flex-shrink-0" />
              <div>
                <h5 className="font-bold text-textMain mb-1">Financial Outlier Management</h5>
                <p className="text-textMuted text-xs leading-relaxed font-sans">
                  The cleaning pipeline identified and removed <strong className="font-semibold text-textMain">{quality?.after.outliers_filtered} extreme salary outliers</strong> using the standard Interquartile Range (IQR) method (thresholds exceeding bounds of Q1 - 1.5 * IQR or Q3 + 1.5 * IQR). This prevents regression parameters in the ML model from distorting.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

    </div>
  );
}
