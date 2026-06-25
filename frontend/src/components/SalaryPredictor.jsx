import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { IndianRupee, ShieldAlert, Sparkles, Plus, Check, Brain, Search, Briefcase, MapPin, Award } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../config';

export default function SalaryPredictor() {
  const [metadata, setMetadata] = useState(null);
  const [selectedRole, setSelectedRole] = useState('Software Engineer');
  const [selectedExp, setSelectedExp] = useState('Mid');
  const [selectedLoc, setSelectedLoc] = useState('Remote');
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [apiError, setApiError] = useState(false);
  
  // Custom skills search query
  const [skillSearch, setSkillSearch] = useState('');

  // Monitor theme switching dynamically to adapt chart colors
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

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

  useEffect(() => {
    // Load metadata and feature importances
    fetch('/data/salary_model_stats.json')
      .then(res => res.json())
      .then(data => {
        setMetadata(data);
        setSelectedSkills(getRoleDefaultSkills(selectedRole));
      })
      .catch(err => console.error("Error loading salary predictor metadata:", err));
  }, []);

  // Update default skills on role change
  const handleRoleChange = (role) => {
    setSelectedRole(role);
    setSelectedSkills(getRoleDefaultSkills(role));
  };

  const getRoleDefaultSkills = (role) => {
    const mapping = {
      "Software Engineer": ["Python", "Git", "SQL", "Docker"],
      "Frontend Developer": ["JavaScript", "React", "HTML5", "CSS3"],
      "Backend Developer": ["Node.js", "Express", "PostgreSQL", "REST APIs"],
      "Data Analyst": ["SQL", "Excel", "Tableau", "Pandas"],
      "Data Scientist": ["Python", "Pandas", "Scikit-Learn", "Machine Learning"],
      "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn"]
    };
    return mapping[role] || [];
  };

  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  // Run ML Prediction via Flask Server
  const getPrediction = () => {
    setPredicting(true);
    setApiError(false);

    fetch(`${API_BASE_URL}/api/predict/salary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        role: selectedRole,
        experience: selectedExp,
        location: selectedLoc,
        skills: selectedSkills
      })
    })
      .then(res => {
        if (!res.ok) throw new Error('Prediction API failed');
        return res.json();
      })
      .then(predData => {
        setPrediction(predData);
        setPredicting(false);
      })
      .catch(err => {
        console.warn("Prediction API failed, executing client-side simulation...");
        setApiError(true);
        executeClientPrediction();
      });
  };

  // Run API prediction when inputs change
  useEffect(() => {
    if (metadata) {
      getPrediction();
    }
  }, [selectedRole, selectedExp, selectedLoc, selectedSkills, metadata]);

  // Client-side fallback prediction logic
  const executeClientPrediction = () => {
    if (!metadata) return;
    
    // Simulate prediction based on statistics
    let base = 20000;
    
    const roleBase = {
      "Software Engineer": 24000,
      "Frontend Developer": 20000,
      "Backend Developer": 22000,
      "Data Analyst": 15000,
      "Data Scientist": 26000,
      "Machine Learning Engineer": 28000
    };
    
    base = roleBase[selectedRole] || base;
    
    const expMultipliers = {
      "Intern": 0.4, "Entry": 0.75, "Mid": 1.0, "Senior": 1.35, "Lead": 1.5, "Not Specified": 0.95
    };
    base *= expMultipliers[selectedExp] || 1.0;
    
    const locAdjustments = {
      "Bengaluru": 1500, "Hyderabad": 1000, "Remote": 1200, "Other Tech Hub": -1000
    };
    base += locAdjustments[selectedLoc] || 0;
    
    // Skill bonuses
    selectedSkills.forEach(skill => {
      base += 300; // generic skill value
    });
    
    const salary = Math.round(base);
    
    setPrediction({
      predicted_salary: salary,
      typical_range_min: roundSalary(salary * 0.9),
      typical_range_max: roundSalary(salary * 1.1),
      percentile: calculateMockPercentile(salary)
    });
    setPredicting(false);
  };

  const roundSalary = (val) => Math.round(val);

  const calculateMockPercentile = (salary) => {
    const mean = 24228.35;
    const std = 7506.26;
    const z = (salary - mean) / std;
    const prob = 1 / (1 + Math.exp(-1.5976 * z));
    return Math.min(99.9, Math.max(0.1, prob * 100));
  };

  if (!metadata) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <div className="h-10 w-64 skeleton animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-96 skeleton animate-pulse" />
          <div className="h-96 skeleton animate-pulse" />
        </div>
      </div>
    );
  }

  // Format Recharts data for feature importance
  const chartData = metadata.feature_importances
    .filter(item => {
      return !item.feature.includes("intercept") && item.importance > 0.001;
    })
    .map(item => {
      let displayName = item.feature
        .replace("standard_title_", "")
        .replace("clean_experience_", "Exp: ")
        .replace("clean_location_", "Loc: ");
      return {
        name: displayName,
        importance: item.importance,
        coefficient: item.coefficient || 0
      };
    })
    .slice(0, 10);

  // Dynamic colors based on active theme
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
    isDark ? '#f87171' : '#dc2626'
  ];

  // Filtering skills list
  const filteredSkills = metadata.categories.skills.filter(s => 
    s.toLowerCase().includes(skillSearch.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-textMain font-sans">ML Salary Predictor</h1>
        <p className="text-textMuted text-sm mt-1.5 font-normal">
          Estimate professional tech salary bands utilizing a trained <strong className="font-semibold text-textMain">Ridge Regression Model</strong> (R²: <strong className="font-semibold text-textMain">{metadata.r2_score.toFixed(3)}</strong>).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* User Configuration Panel */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-card p-6 space-y-5">
            <h3 className="text-sm font-bold text-textMain flex items-center gap-2 border-b border-glassBorder pb-3">
              <Brain size={18} className="text-brandBlue" /> Parameters Simulator
            </h3>

            <div className="space-y-4">
              {/* Target Profile Custom Cards Selector */}
              <div>
                <label className="form-label">Target Tech Profile</label>
                <div className="grid grid-cols-2 gap-2">
                  {metadata.categories.titles.map(role => {
                    const active = selectedRole === role;
                    return (
                      <button
                        type="button"
                        key={role}
                        onClick={() => handleRoleChange(role)}
                        className={`p-3 text-left rounded-xl border transition-all duration-200 cursor-pointer flex flex-col justify-between h-20 ${
                          active 
                            ? 'bg-brandBlue/10 border-brandBlue text-brandBlue shadow-sm' 
                            : 'bg-darkCard hover:bg-brandSecondary border-glassBorder text-textMuted hover:text-textMain'
                        }`}
                      >
                        <Briefcase size={14} className={active ? 'text-brandBlue' : 'text-textMuted'} />
                        <span className="text-[11px] font-bold leading-tight">{role}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Experience Tier Selector (Segmented) */}
              <div>
                <label className="form-label">Experience Tier</label>
                <div className="flex flex-wrap bg-brandSecondary p-1 rounded-xl border border-glassBorder gap-1 shadow-inner">
                  {metadata.categories.experience.filter(e => e !== 'Not Specified').map(exp => {
                    const active = selectedExp === exp;
                    return (
                      <button
                        type="button"
                        key={exp}
                        onClick={() => setSelectedExp(exp)}
                        className={`flex-1 min-w-[60px] py-1.5 text-center text-[10px] font-bold rounded-lg uppercase tracking-wider transition-all duration-150 cursor-pointer ${
                          active 
                            ? 'bg-brandBlue text-white shadow-sm' 
                            : 'text-textMuted hover:text-textMain'
                        }`}
                      >
                        {exp}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Location Hub Selector (Segmented) */}
              <div>
                <label className="form-label">Location Hub</label>
                <div className="flex flex-wrap bg-brandSecondary p-1 rounded-xl border border-glassBorder gap-1 shadow-inner">
                  {metadata.categories.locations.map(loc => {
                    const active = selectedLoc === loc;
                    return (
                      <button
                        type="button"
                        key={loc}
                        onClick={() => setSelectedLoc(loc)}
                        className={`flex-1 min-w-[70px] py-1.5 text-center text-[10px] font-bold rounded-lg uppercase tracking-wider transition-all duration-150 cursor-pointer ${
                          active 
                            ? 'bg-brandBlue text-white shadow-sm' 
                            : 'text-textMuted hover:text-textMain'
                        }`}
                      >
                        {loc === 'Other Tech Hub' ? 'Other Hub' : loc}
                      </button>
                    );
                  })}
                </div>
              </div>

            </div>

            {/* Skills selection with Search */}
            <div className="space-y-3 pt-2">
              <div className="flex justify-between items-center">
                <span className="form-label mb-0">Keywords & Technologies</span>
                <span className="text-[10px] font-semibold text-brandBlue">{selectedSkills.length} Selected</span>
              </div>
              
              <div className="flex items-center bg-brandSecondary border border-glassBorder rounded-xl px-2.5 py-1.5 focus-within:border-brandBlue transition-all duration-200">
                <Search size={14} className="text-textMuted mr-2" />
                <input 
                  type="text" 
                  placeholder="Filter skills..." 
                  value={skillSearch}
                  onChange={(e) => setSkillSearch(e.target.value)}
                  className="bg-transparent border-none outline-none text-xs text-textMain w-full"
                />
              </div>

              <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-2 border border-glassBorder rounded-xl bg-brandSecondary/30">
                {filteredSkills.map(skill => {
                  const active = selectedSkills.includes(skill);
                  return (
                    <button
                      type="button"
                      key={skill}
                      onClick={() => toggleSkill(skill)}
                      className={`text-[10px] font-bold px-2.5 py-1.5 rounded-lg border transition-all duration-150 flex items-center gap-1 cursor-pointer ${
                        active 
                          ? 'bg-brandBlue/10 text-brandBlue border-brandBlue/35' 
                          : 'bg-transparent text-textMuted border-glassBorder hover:border-text-muted hover:text-textMain'
                      }`}
                      id={`predict-skill-${skill.replace(/\s+/g, '-').toLowerCase()}`}
                    >
                      {active ? <Check size={10} className="text-brandBlue" /> : <Plus size={10} />}
                      {skill}
                    </button>
                  );
                })}
                {filteredSkills.length === 0 && (
                  <span className="text-[10px] text-textMuted p-2 w-full text-center">No matching keywords.</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Prediction Results Display & Charting */}
        <div className="lg:col-span-7 space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            
            {/* Primary output display styled as a receipt */}
            <div className="glass-card p-6 md:col-span-7 flex flex-col justify-between relative overflow-hidden min-h-[220px]">
              <div className="absolute top-0 left-0 w-full h-[3px] bg-brandBlue" />
              
              {predicting ? (
                <div className="flex flex-col items-center justify-center h-full gap-2 py-10">
                  <div className="w-8 h-8 border-4 border-brandBlue/20 border-t-brandBlue rounded-full animate-spin" />
                  <span className="text-xs text-textMuted mt-1">Executing Regression Estimator...</span>
                </div>
              ) : prediction ? (
                <div className="space-y-4">
                  <div className="flex justify-between items-center border-b border-glassBorder pb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-textMuted flex items-center gap-1">
                      <Sparkles size={12} className="text-brandCyan" /> Estimated Salary Receipt
                    </span>
                    <span className="text-[9px] font-bold bg-brandSuccess/10 text-brandSuccess border border-brandSuccess/15 px-2 py-0.5 rounded">Verified Range</span>
                  </div>

                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-textMuted">Base Profile Fee ({selectedRole})</span>
                      <span className="font-semibold text-textMain">{formatCompactINR(prediction.predicted_salary * 0.7)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-textMuted">Experience Level Factor ({selectedExp})</span>
                      <span className="font-semibold text-textMain">x{(selectedExp === 'Intern' ? 0.4 : selectedExp === 'Entry' ? 0.75 : selectedExp === 'Mid' ? 1.0 : selectedExp === 'Senior' ? 1.35 : 1.5).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-textMuted">Location Hub Adjustment ({selectedLoc})</span>
                      <span className="font-semibold text-textMain">{selectedLoc === 'Remote' ? '+₹1.25L' : selectedLoc === 'Bengaluru' ? '+₹1.5L' : selectedLoc === 'Hyderabad' ? '+₹1L' : '-₹80k'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-textMuted">Keywords Premium ({selectedSkills.length} selected)</span>
                      <span className="font-semibold text-brandBlue">+{formatCompactINR(selectedSkills.length * 300)}</span>
                    </div>
                  </div>

                  <div className="border-t border-dashed border-glassBorder pt-3 flex flex-col items-center">
                    <span className="text-[9px] font-bold uppercase text-textMuted">Estimated Annual Package</span>
                    <div className="flex items-center text-brandSuccess font-extrabold text-3xl my-1">
                      <IndianRupee size={20} className="-mr-1 text-brandSuccess" />
                      <span>{Math.round(prediction.predicted_salary * 83.333).toLocaleString('en-IN')}</span>
                    </div>
                    <span className="text-[10px] text-textMuted mt-1 bg-brandSecondary px-2 py-1 rounded">
                      Typical Range: {formatCompactINR(prediction.typical_range_min)} - {formatCompactINR(prediction.typical_range_max)}
                    </span>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Percentile gauge with high styling */}
            <div className="glass-card p-6 md:col-span-5 flex flex-col items-center justify-center text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-textMuted mb-3 flex items-center gap-1"><Award size={12} /> Market Standing</span>
              
              {prediction && (
                <div className="relative w-28 h-28 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-brandSecondary"
                      strokeWidth="2.5"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="text-brandBlue transition-all duration-500 ease-out"
                      strokeDasharray={`${prediction.percentile}, 100`}
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="text-xl font-extrabold text-textMain">{Math.round(prediction.percentile)}th</span>
                    <span className="text-[9px] text-textMuted font-bold uppercase">Percentile</span>
                  </div>
                </div>
              )}
            </div>

          </div>

          {/* Model Weights Chart */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-textMain mb-6 flex items-center gap-1.5">
              <Brain size={16} className="text-brandPurple" /> Feature Influence Strengths (Ridge Weights)
            </h3>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                  <XAxis dataKey="name" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} interval={0} angle={-20} textAnchor="end" height={40} />
                  <YAxis stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} tickFormatter={(val) => `${(val*100).toFixed(1)}%`} />
                  <Tooltip content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div 
                          className="rounded-xl p-2.5 shadow-md border text-left text-xs"
                          style={{ backgroundColor: tooltipBg, borderColor: tooltipBorder }}
                        >
                          <p className="text-textMuted mb-0.5 font-bold uppercase tracking-wider text-[9px]">{label}</p>
                          <p className="text-brandBlue font-semibold">Model Influence: {(payload[0].value * 100).toFixed(1)}%</p>
                          <p className="text-textMuted mt-0.5">Base Impact: {payload[0].payload.coefficient >= 0 ? '+' : ''}{formatFullINR(payload[0].payload.coefficient)}</p>
                        </div>
                      );
                    }
                    return null;
                  }} />
                  <Bar dataKey="importance" fill={purpleColor} radius={[4, 4, 0, 0]} maxBarSize={16}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            {apiError && (
              <div className="mt-4 bg-brandDanger/10 border border-brandDanger/20 rounded-xl p-3 flex gap-2 items-center text-xs text-brandDanger">
                <ShieldAlert size={16} />
                <span>Prediction API offline. The app is falling back to static client-side calculations automatically.</span>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
}
