import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Award, ShieldAlert, Sparkles, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../config';

export default function PlacementAnalytics() {
  const [cgpa, setCgpa] = useState(7.0);
  const [skillsCount, setSkillsCount] = useState(5);
  const [internships, setInternships] = useState(0);
  const [projects, setProjects] = useState(0);
  const [certifications, setCertifications] = useState(0);

  const [results, setResults] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const [importance, setImportance] = useState([]);
  const [apiError, setApiError] = useState(false);

  // Monitor theme switching dynamically to adapt colors
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    // Load feature importances
    fetch('/data/placement_model_stats.json')
      .then(res => res.json())
      .then(data => {
        if (data.feature_importances) {
          // Clean labels
          const cleaned = data.feature_importances.map(item => ({
            feature: item.feature
              .replace("cgpa", "CGPA")
              .replace("skills_count", "Skills Count")
              .replace("internships", "Internships")
              .replace("projects", "Projects")
              .replace("certifications", "Certifications"),
            importance: item.importance
          }));
          setImportance(cleaned);
        }
      })
      .catch(err => console.error("Error loading placement model stats:", err));
  }, []);

  const runSimulation = () => {
    setSimulating(true);
    setApiError(false);

    fetch(`${API_BASE_URL}/api/predict/placement`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cgpa: parseFloat(cgpa),
        skills_count: intVal(skillsCount),
        internships: intVal(internships),
        projects: intVal(projects),
        certifications: intVal(certifications)
      })
    })
      .then(res => {
        if (!res.ok) throw new Error('Placement API failed');
        return res.json();
      })
      .then(simData => {
        setResults(simData);
        setSimulating(false);
      })
      .catch(err => {
        console.warn("Placement API offline, running client-side logit model fallback...");
        setApiError(true);
        executeClientSimulation();
      });
  };

  const intVal = (v) => intValSecure(v);
  const intValSecure = (val) => parseInt(val);

  // Client-side Logit Equation (aligned with Datasets/generate_dataset.py logic)
  const executeClientSimulation = () => {
    // logit = -7.5 + 0.95*cgpa + 1.6*internships + 0.75*projects + 0.5*certifications + 0.1*skills
    const logit = -7.5 + (0.95 * cgpa) + (1.6 * internships) + (0.75 * projects) + (0.5 * certifications) + (0.1 * skillsCount);
    const prob = 1 / (1 + Math.exp(-logit));
    const score = Math.round(prob * 100);

    const suggestions = [];
    if (cgpa < 7.5) {
      suggestions.push("Academic Filter: Your CGPA is below the typical 7.5 threshold for premier companies. Focus on lifting your academic standing.");
    }
    if (internships === 0) {
      suggestions.push("Experience Gap: Highlight involvement in virtual internships, open-source programs, or freelancing to get professional milestones on paper.");
    }
    if (projects < 2) {
      suggestions.push("Project Portfolio: Recruiters look for at least 2 full-stack projects. Ensure yours are hosted on GitHub with detailed READMEs.");
    }
    if (certifications === 0) {
      suggestions.push("Skills Validation: Acquire cloud/data credentials (e.g. AWS Practitioner, Snowflake) to validate your tech stack to screeners.");
    }
    if (suggestions.length === 0) {
      suggestions.push("Highly Competitive: Profile is highly competitive! Focus on refining system design and coding mock interviews to clear final rounds.");
    }

    const fallbackImportance = [
      { feature: "Internships", importance: 0.40 },
      { feature: "CGPA", importance: 0.30 },
      { feature: "Projects", importance: 0.15 },
      { feature: "Certifications", importance: 0.10 },
      { feature: "Skills Count", importance: 0.05 }
    ];

    setResults({
      placement_probability: prob,
      employability_score: score,
      suggestions: suggestions
    });
    
    if (importance.length === 0) {
      setImportance(fallbackImportance);
    }
    setSimulating(false);
  };

  // Re-run simulation when parameters change
  useEffect(() => {
    runSimulation();
  }, [cgpa, skillsCount, internships, projects, certifications]);

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-brandSuccess';
    if (score >= 50) return 'text-brandWarning';
    return 'text-brandDanger';
  };

  const getScoreStroke = (score) => {
    if (score >= 75) return 'text-brandSuccess';
    if (score >= 50) return 'text-brandWarning';
    return 'text-brandDanger';
  };

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
    isDark ? '#fbbf24' : '#d97706'
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      
      {/* Title */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-textMain font-sans">Placement Analytics</h1>
        <p className="text-textMuted text-sm mt-1.5 font-normal">
          Adjust academic metrics and experience profiles to dynamically forecast placement probabilities using the trained Random Forest classifier.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Simulator Sliders (Left Panel) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-card p-6 space-y-6">
            <h3 className="text-sm font-bold text-textMain flex items-center gap-2 border-b border-glassBorder pb-3">
              <Sparkles size={18} className="text-brandBlue" /> Profile Parameter Simulator
            </h3>

            {/* CGPA */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="form-label mb-0 font-medium">Cumulative GPA (CGPA)</span>
                <span className="text-brandBlue font-bold bg-brandBlue/10 px-2 py-0.5 rounded">{cgpa.toFixed(2)}</span>
              </div>
              <input 
                type="range" 
                min="5.5" 
                max="10.0" 
                step="0.05"
                value={cgpa}
                onChange={(e) => setCgpa(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-brandSecondary rounded-lg appearance-none cursor-pointer accent-brandBlue"
                id="slider-cgpa"
              />
            </div>

            {/* Skills count */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="form-label mb-0 font-medium">Core Technologies Count</span>
                <span className="text-brandCyan font-bold bg-brandCyan/10 px-2 py-0.5 rounded">{skillsCount} skills</span>
              </div>
              <input 
                type="range" 
                min="3" 
                max="15" 
                step="1"
                value={skillsCount}
                onChange={(e) => setSkillsCount(parseInt(e.target.value))}
                className="w-full h-1.5 bg-brandSecondary rounded-lg appearance-none cursor-pointer accent-brandCyan"
                id="slider-skills"
              />
            </div>

            {/* Internships, Projects, Certifications Controls (Segmented design) */}
            <div className="grid grid-cols-3 gap-3 pt-2">
              <div className="flex flex-col items-center justify-between bg-brandSecondary/60 border border-glassBorder rounded-xl p-3 text-center">
                <span className="text-[10px] font-bold text-textMuted uppercase mb-2">Internships</span>
                <span className="text-lg font-extrabold text-textMain mb-2">{internships}</span>
                <div className="flex gap-1">
                  <button 
                    type="button"
                    onClick={() => setInternships(Math.max(0, internships - 1))}
                    className="w-6 h-6 rounded-md bg-darkCard border border-glassBorder hover:bg-brandSecondary text-xs font-bold text-textMain flex items-center justify-center cursor-pointer"
                    id="btn-internship-dec"
                  >-</button>
                  <button 
                    type="button"
                    onClick={() => setInternships(Math.min(3, internships + 1))}
                    className="w-6 h-6 rounded-md bg-darkCard border border-glassBorder hover:bg-brandSecondary text-xs font-bold text-textMain flex items-center justify-center cursor-pointer"
                    id="btn-internship-inc"
                  >+</button>
                </div>
              </div>

              <div className="flex flex-col items-center justify-between bg-brandSecondary/60 border border-glassBorder rounded-xl p-3 text-center">
                <span className="text-[10px] font-bold text-textMuted uppercase mb-2">Projects</span>
                <span className="text-lg font-extrabold text-textMain mb-2">{projects}</span>
                <div className="flex gap-1">
                  <button 
                    type="button"
                    onClick={() => setProjects(Math.max(0, projects - 1))}
                    className="w-6 h-6 rounded-md bg-darkCard border border-glassBorder hover:bg-brandSecondary text-xs font-bold text-textMain flex items-center justify-center cursor-pointer"
                    id="btn-projects-dec"
                  >-</button>
                  <button 
                    type="button"
                    onClick={() => setProjects(Math.min(5, projects + 1))}
                    className="w-6 h-6 rounded-md bg-darkCard border border-glassBorder hover:bg-brandSecondary text-xs font-bold text-textMain flex items-center justify-center cursor-pointer"
                    id="btn-projects-inc"
                  >+</button>
                </div>
              </div>

              <div className="flex flex-col items-center justify-between bg-brandSecondary/60 border border-glassBorder rounded-xl p-3 text-center">
                <span className="text-[10px] font-bold text-textMuted uppercase mb-2">Certs</span>
                <span className="text-lg font-extrabold text-textMain mb-2">{certifications}</span>
                <div className="flex gap-1">
                  <button 
                    type="button"
                    onClick={() => setCertifications(Math.max(0, certifications - 1))}
                    className="w-6 h-6 rounded-md bg-darkCard border border-glassBorder hover:bg-brandSecondary text-xs font-bold text-textMain flex items-center justify-center cursor-pointer"
                    id="btn-certs-dec"
                  >-</button>
                  <button 
                    type="button"
                    onClick={() => setCertifications(Math.min(3, certifications + 1))}
                    className="w-6 h-6 rounded-md bg-darkCard border border-glassBorder hover:bg-brandSecondary text-xs font-bold text-textMain flex items-center justify-center cursor-pointer"
                    id="btn-certs-inc"
                  >+</button>
                </div>
              </div>
            </div>

            {/* Informational Callout */}
            <div className="bg-brandBlue/5 border border-brandBlue/15 rounded-xl p-3.5 text-[11px] leading-relaxed text-textMuted font-sans">
              💡 <strong className="font-semibold text-textMain">What-If Simulation:</strong> Shift the CGPA slider or adjust the counters. The Random Forest classifier evaluates these metrics and re-computes your placement probability score dynamically.
            </div>
          </div>
        </div>

        {/* Results Panel & Feature Importances (Right Panel) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            
            {/* Probability Gauge Dial */}
            <div className="glass-card p-6 md:col-span-7 flex flex-col items-center justify-center text-center relative overflow-hidden min-h-[220px]">
              <div className="absolute top-0 left-0 w-full h-[3px] bg-brandBlue" />
              
              {simulating ? (
                <div className="flex flex-col items-center justify-center h-full gap-2 py-10">
                  <div className="w-8 h-8 border-4 border-brandBlue/20 border-t-brandBlue rounded-full animate-spin" />
                  <span className="text-xs text-textMuted mt-1">Recalculating Classifier Likelihood...</span>
                </div>
              ) : results ? (
                <>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-textMuted flex items-center gap-1.5">
                    <FileText size={14} className="text-brandSuccess" /> Placement Likelihood
                  </span>
                  
                  <div className="relative w-28 h-28 flex items-center justify-center my-2">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-brandSecondary"
                        strokeWidth="2.5"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className={`transition-all duration-500 ease-out ${getScoreStroke(results.employability_score)}`}
                        strokeDasharray={`${results.employability_score}, 100`}
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <div className="absolute flex flex-col items-center justify-center">
                      <span className={`text-2xl font-black ${getScoreColor(results.employability_score)}`}>{results.employability_score}%</span>
                      <span className="text-[8px] text-textMuted font-bold uppercase tracking-wider">Probability</span>
                    </div>
                  </div>
                  
                  <div className="bg-brandSecondary border border-glassBorder rounded-lg px-3 py-1 text-xs text-textMuted font-medium">
                    Status: <strong className={getScoreColor(results.employability_score)}>{
                      results.employability_score >= 75 ? 'Highly Employable' : results.employability_score >= 50 ? 'Average Fit' : 'Skills Deficit'
                    }</strong>
                  </div>
                </>
              ) : null}
            </div>

            {/* Key Suggestions list (Styled as scorecard checklist) */}
            <div className="glass-card p-5 md:col-span-5 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-textMuted mb-3 flex items-center gap-1.5">
                <AlertCircle size={14} className="text-brandWarning" /> Key Gaps Identified
              </span>
              
              <div className="text-[11px] space-y-3 max-h-40 overflow-y-auto pr-1">
                {results && results.suggestions.map((sug, idx) => (
                  <div key={idx} className="flex gap-2 items-start text-textMuted leading-relaxed font-sans border-b border-glassBorder pb-1.5 last:border-0 last:pb-0">
                    <CheckCircle2 size={12} className="text-brandBlue mt-0.5 flex-shrink-0" />
                    <span>{sug}</span>
                  </div>
                ))}
              </div>
              <span className="text-[9px] text-textMuted leading-tight block border-t border-glassBorder pt-2 mt-2">
                *Improvements shift placement probability bands immediately.
              </span>
            </div>

          </div>

          {/* Feature Importances of Decision Tree Model */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-textMain mb-6 flex items-center gap-1.5 border-b border-glassBorder pb-3">
              <Award size={16} className="text-brandPurple" /> Classifier Decision Weighting (Random Forest Feature Importance)
            </h3>
            
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={importance} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                  <XAxis type="number" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} tickFormatter={(val) => `${(val*100).toFixed(0)}%`} />
                  <YAxis type="category" dataKey="feature" stroke={textColor} tick={{ fontSize: 9, fontFamily: 'Inter' }} />
                  <Tooltip content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div 
                          className="rounded-xl p-2 shadow-md border text-xs"
                          style={{ backgroundColor: tooltipBg, borderColor: tooltipBorder }}
                        >
                          <p className="text-brandBlue font-semibold">{label}: {(payload[0].value * 100).toFixed(1)}% influence</p>
                        </div>
                      );
                    }
                    return null;
                  }} />
                  <Bar dataKey="importance" fill={tealColor} radius={[0, 4, 4, 0]} maxBarSize={14}>
                    {importance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            {apiError && (
              <div className="mt-4 bg-brandDanger/10 border border-brandDanger/20 rounded-xl p-3 flex gap-2 items-center text-xs text-brandDanger">
                <ShieldAlert size={16} />
                <span>Flask Classifier offline. Running client-side logit simulator values.</span>
              </div>
            )}
          </div>

        </div>

      </div>

      <style>{`
        input[type="range"]::-webkit-slider-thumb {
          box-shadow: 0 0 8px rgba(79, 70, 229, 0.4);
          background-color: var(--color-primary);
        }
      `}</style>
    </div>
  );
}

const COLORS = ['#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];
