import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area, Legend 
} from 'recharts';
import { 
  Briefcase, DollarSign, MapPin, Activity, Filter, Search, Sparkles, Globe 
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [selectedRole, setSelectedRole] = useState('Data Analyst');
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [expFilter, setExpFilter] = useState('All');
  const [locFilter, setLocFilter] = useState('All');
  
  useEffect(() => {
    // Load static data exported by Python pipeline
    fetch('/data/market_stats.json')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        if (data.role_stats && data.role_stats.length > 0) {
          setSelectedRole(data.role_stats[0].standard_title);
        }
      })
      .catch(err => console.error("Error loading market stats:", err));

    fetch('/data/cleaned_jobs_sample.json')
      .then(res => res.json())
      .then(data => setJobs(data))
      .catch(err => console.error("Error loading sample jobs:", err));
  }, []);

  if (!stats || jobs.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', flexDirection: 'column', gap: '16px' }}>
        <div style={{ width: '40px', height: '40px', border: '4px solid rgba(59, 130, 246, 0.2)', borderTop: '4px solid #3b82f6', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>Analyzing marketplace intelligence data...</p>
        <style>{`
          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        `}</style>
      </div>
    );
  }

  // Pre-calculate dropdown filter options from jobs
  const rolesList = ['All', ...new Set(jobs.map(j => j.standard_title))];
  const expList = ['All', ...new Set(jobs.map(j => j.clean_experience))].filter(e => e !== '');
  const locList = ['All', ...new Set(jobs.map(j => j.clean_location))];

  // Filtered jobs sample
  const filteredJobs = jobs.filter(job => {
    const matchesSearch = 
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.skills_extracted.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));
      
    const matchesRole = roleFilter === 'All' || job.standard_title === roleFilter;
    const matchesExp = expFilter === 'All' || job.clean_experience === expFilter;
    const matchesLoc = locFilter === 'All' || job.clean_location === locFilter;
    
    return matchesSearch && matchesRole && matchesExp && matchesLoc;
  });

  // Recharts color palette
  const COLORS = ['#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

  // Prepare skill distribution for the selected role
  const roleSkillData = stats.skills_by_role[selectedRole] || [];

  return (
    <div className="fade-in-section" id="dashboard-view">
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 className="gradient-text" style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>Market Intelligence Dashboard</h1>
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>
          Interactive analysis of <strong>{stats.total_jobs.toLocaleString()}</strong> tech job postings. Cleaned and processed via Python Pandas pipeline.
        </p>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        
        <div className="glass-card metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: '500' }}>Analyzed Listings</span>
            <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '6px', borderRadius: '8px' }}>
              <Briefcase size={20} color="#3b82f6" />
            </div>
          </div>
          <h3 style={{ fontSize: '28px', fontWeight: '700', margin: '4px 0' }}>{stats.total_jobs.toLocaleString()}</h3>
          <span style={{ color: '#10b981', fontSize: '12px', fontWeight: '500' }}>✓ 100% Cleaned & De-duplicated</span>
        </div>

        <div className="glass-card metric-card purple">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: '500' }}>Avg Tech Salary</span>
            <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '6px', borderRadius: '8px' }}>
              <DollarSign size={20} color="#8b5cf6" />
            </div>
          </div>
          <h3 style={{ fontSize: '28px', fontWeight: '700', margin: '4px 0' }}>${stats.avg_salary_global.toLocaleString()}</h3>
          <span style={{ color: '#94a3b8', fontSize: '12px' }}>Annual Global USD Equivalent</span>
        </div>

        <div className="glass-card metric-card cyan">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: '500' }}>Remote Job Ratio</span>
            <div style={{ background: 'rgba(6, 182, 212, 0.1)', padding: '6px', borderRadius: '8px' }}>
              <Globe size={20} color="#06b6d4" />
            </div>
          </div>
          <h3 style={{ fontSize: '28px', fontWeight: '700', margin: '4px 0' }}>{stats.remote_percentage}%</h3>
          <span style={{ color: '#06b6d4', fontSize: '12px', fontWeight: '500' }}>Full/Partial Work From Home</span>
        </div>

        <div className="glass-card metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: '500' }}>Top Demand Skill</span>
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '6px', borderRadius: '8px' }}>
              <Activity size={20} color="#10b981" />
            </div>
          </div>
          <h3 style={{ fontSize: '28px', fontWeight: '700', margin: '4px 0' }}>{stats.top_skills[0]?.skill || 'Python'}</h3>
          <span style={{ color: '#94a3b8', fontSize: '12px' }}>Appears in {Math.round((stats.top_skills[0]?.count / stats.total_jobs) * 100)}% of postings</span>
        </div>

      </div>

      {/* Main Charts Area */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        
        {/* Salary Ranges by Role */}
        <div className="glass-card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <DollarSign size={18} color="#3b82f6" /> Average Salary by Standard Job Title
          </h3>
          <div style={{ width: '100%', height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.role_stats} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSalary" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="standard_title" stroke="#64748b" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(val) => `$${val/1000}k`} />
                <Tooltip 
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="custom-recharts-tooltip">
                          <p className="label">{label}</p>
                          <p className="value" style={{ color: '#3b82f6' }}>Avg Salary: ${payload[0].value.toLocaleString()}</p>
                          <p style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>Jobs: {payload[0].payload.job_count}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area type="monotone" dataKey="avg_salary" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorSalary)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dynamic Skill Demand by Role */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} color="#06b6d4" /> Skill Demand for:
            </h3>
            <select 
              className="custom-select" 
              style={{ width: 'auto', padding: '6px 12px', fontSize: '14px' }}
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              id="skill-role-selector"
            >
              {stats.role_stats.map(r => (
                <option key={r.standard_title} value={r.standard_title}>{r.standard_title}</option>
              ))}
            </select>
          </div>
          <div style={{ width: '100%', height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleSkillData} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="skill" stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip 
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="custom-recharts-tooltip">
                          <p className="label">{label}</p>
                          <p className="value" style={{ color: '#06b6d4' }}>Frequency: {payload[0].value} jobs</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]}>
                  {roleSkillData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Secondary Row Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        
        {/* Remote vs In-person Salary Premium */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px' }}>Remote Work Distribution</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1, minHeight: '200px' }}>
            <div style={{ width: '180px', height: '180px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.remote_stats}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={5}
                    dataKey="job_count"
                  >
                    {stats.remote_stats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#06b6d4' : '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="custom-recharts-tooltip">
                            <p className="label">{payload[0].name}</p>
                            <p className="value">Count: {payload[0].value.toLocaleString()}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ marginLeft: '20px' }}>
              {stats.remote_stats.map((item, idx) => (
                <div key={item.clean_remote} style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: idx === 0 ? '#06b6d4' : '#64748b' }} />
                    <span style={{ fontWeight: '500', fontSize: '14px' }}>{item.clean_remote}</span>
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: '13px', marginLeft: '20px' }}>
                    Avg: ${item.avg_salary.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Experience Level Distributions */}
        <div className="glass-card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px' }}>Demands & Salary by Experience Level</h3>
          <div style={{ width: '100%', height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.experience_stats} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="clean_experience" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(val) => `$${val/1000}k`} />
                <Tooltip 
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="custom-recharts-tooltip">
                          <p className="label">{label} Level</p>
                          <p className="value" style={{ color: '#8b5cf6' }}>Avg Salary: ${payload[0].value.toLocaleString()}</p>
                          <p style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>Listings: {payload[0].payload.job_count}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="avg_salary" fill="#8b5cf6" radius={[4, 4, 0, 0]} maxBarSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Global Geographic Hubs */}
        <div className="glass-card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px' }}>Distribution by Geographic Hub</h3>
          <div style={{ width: '100%', height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.location_stats.sort((a,b)=>b.job_count - a.job_count).slice(0, 6)} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="clean_location" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip 
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="custom-recharts-tooltip">
                          <p className="label">{label}</p>
                          <p className="value" style={{ color: '#10b981' }}>Jobs Count: {payload[0].value}</p>
                          <p style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>Avg Salary: ${payload[0].payload.avg_salary.toLocaleString()}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="job_count" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Interactive Cleaned Jobs Explorer Table */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '4px' }}>Processed Jobs Browser</h3>
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>Cleaned and structured records from the pipeline. Search keywords or filter dynamically.</p>
          </div>
          
          {/* Search Box */}
          <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-secondary)', border: '1px solid var(--card-border)', borderRadius: '10px', padding: '6px 12px', width: '280px' }}>
            <Search size={18} color="#64748b" style={{ marginRight: '8px' }} />
            <input 
              type="text" 
              placeholder="Search roles, companies, skills..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ background: 'none', border: 'none', outline: 'none', color: 'white', width: '100%', fontSize: '14px' }}
              id="job-search-input"
            />
          </div>
        </div>

        {/* Filters Controls Row */}
        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '150px' }}>
            <span style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>Role Profile</span>
            <select className="custom-select" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} id="filter-role-select">
              {rolesList.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          
          <div style={{ flex: 1, minWidth: '150px' }}>
            <span style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>Experience Tier</span>
            <select className="custom-select" value={expFilter} onChange={(e) => setExpFilter(e.target.value)} id="filter-experience-select">
              {expList.map(e => <option key={e} value={e}>{e === 'All' ? 'All Experience Levels' : e}</option>)}
            </select>
          </div>

          <div style={{ flex: 1, minWidth: '150px' }}>
            <span style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>Office Location</span>
            <select className="custom-select" value={locFilter} onChange={(e) => setLocFilter(e.target.value)} id="filter-location-select">
              {locList.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        </div>

        {/* Jobs List Grid */}
        <div style={{ overflowX: 'auto', border: '1px solid var(--card-border)', borderRadius: '12px', background: 'rgba(8, 12, 20, 0.4)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '800px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--card-border)', background: 'rgba(255,255,255,0.01)' }}>
                <th style={{ padding: '16px', color: '#64748b', fontSize: '13px', fontWeight: '600' }}>Job Title</th>
                <th style={{ padding: '16px', color: '#64748b', fontSize: '13px', fontWeight: '600' }}>Company</th>
                <th style={{ padding: '16px', color: '#64748b', fontSize: '13px', fontWeight: '600' }}>Location & Workplace</th>
                <th style={{ padding: '16px', color: '#64748b', fontSize: '13px', fontWeight: '600' }}>Experience</th>
                <th style={{ padding: '16px', color: '#64748b', fontSize: '13px', fontWeight: '600' }}>Estimated Salary</th>
                <th style={{ padding: '16px', color: '#64748b', fontSize: '13px', fontWeight: '600' }}>Identified Skills</th>
              </tr>
            </thead>
            <tbody>
              {filteredJobs.slice(0, 10).map((job) => (
                <tr key={job.job_id} style={{ borderBottom: '1px solid var(--card-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '16px', fontWeight: '500' }}>{job.title}</td>
                  <td style={{ padding: '16px', color: '#cbd5e1' }}>{job.company}</td>
                  <td style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '14px' }}>
                        <MapPin size={14} color="#64748b" /> {job.clean_location}
                      </span>
                      {job.clean_remote ? (
                        <span className="badge remote">Remote</span>
                      ) : (
                        <span className="badge onsite">On-Site</span>
                      )}
                    </div>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ fontSize: '14px', textTransform: 'capitalize' }}>{job.clean_experience}</span>
                  </td>
                  <td style={{ padding: '16px', fontWeight: '600', color: '#10b981' }}>
                    ${Math.round(job.salary_min/1000)}k - ${Math.round(job.salary_max/1000)}k
                  </td>
                  <td style={{ padding: '16px', maxWidth: '300px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {job.skills_extracted.slice(0, 3).map(skill => (
                        <span key={skill} className="skill-tag" style={{ padding: '2px 6px', fontSize: '10px' }}>{skill}</span>
                      ))}
                      {job.skills_extracted.length > 3 && (
                        <span style={{ fontSize: '11px', color: '#64748b', alignSelf: 'center' }}>+{job.skills_extracted.length - 3} more</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {filteredJobs.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
                    No postings match the active search and filter settings.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {filteredJobs.length > 10 && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px', color: '#64748b', fontSize: '14px' }}>
            Showing top 10 of {filteredJobs.length} matching entries.
          </div>
        )}
      </div>
      
      <style>{`
        .table-row-hover:hover {
          background: rgba(255, 255, 255, 0.02);
        }
      `}</style>
    </div>
  );
}
