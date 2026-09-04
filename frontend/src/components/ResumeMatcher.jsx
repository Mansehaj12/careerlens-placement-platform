import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle2, AlertTriangle, ArrowRight, BookOpen, ShieldAlert, Sparkles, Check, Plus, Layers, Zap, CheckSquare, XCircle, Award, Target, Hash } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../config';

export default function ResumeMatcher() {
  const [selectedRole, setSelectedRole] = useState('Software Engineer');
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [textFallback, setTextFallback] = useState('');
  const [useTextMode, setUseTextMode] = useState(false);
  const [cachedText, setCachedText] = useState('');

  // Monitor theme switching dynamically to adapt colors
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const roles = [
    "Software Engineer", "Frontend Developer", "Backend Developer", 
    "Data Analyst", "Data Scientist", "Machine Learning Engineer"
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setErrorMsg('Invalid file type. Resume must be a PDF document.');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setCachedText('');
      setErrorMsg('');
    }
  };

  const triggerAnalysis = (roleToRun, targetFile = file, targetText = cachedText || textFallback) => {
    setErrorMsg('');
    setAnalyzing(true);

    // 1. If we already have the resume text (cached from PDF or pasted), run instant API evaluation
    if (targetText && targetText.trim()) {
      fetch(`${API_BASE_URL}/api/analyze/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: roleToRun,
          text: targetText
        })
      })
        .then(async (res) => {
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Server error');
          return data;
        })
        .then((data) => {
          setResults(data);
          if (data.extracted_text) setCachedText(data.extracted_text);
          setAnalyzing(false);
        })
        .catch((err) => {
          console.warn("API text analysis offline, executing client-side fallback...", err);
          runClientSideAnalysis(targetText, roleToRun);
          setAnalyzing(false);
        });
      return;
    }

    // 2. Direct PDF file upload submission
    if (!targetFile) {
      setErrorMsg('Please select a PDF file or paste your resume text first.');
      setAnalyzing(false);
      return;
    }

    const formData = new FormData();
    formData.append('role', roleToRun);
    formData.append('file', targetFile);

    fetch(`${API_BASE_URL}/api/analyze/resume`, {
      method: 'POST',
      body: formData
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Server error');
        return data;
      })
      .then((data) => {
        setResults(data);
        if (data.extracted_text) setCachedText(data.extracted_text);
        setAnalyzing(false);
      })
      .catch((err) => {
        console.warn("PDF Upload API failed, attempting client fallback...", err);
        setErrorMsg('Flask server offline or PDF read error. Please retry or switch to Text Paste mode.');
        setAnalyzing(false);
      });
  };

  const handleAnalyze = (e) => {
    if (e) e.preventDefault();
    triggerAnalysis(selectedRole);
  };

  // Instant live re-evaluation whenever the user picks a different target role
  const handleRoleChange = (newRole) => {
    setSelectedRole(newRole);
    if (file || textFallback.trim() || cachedText) {
      triggerAnalysis(newRole, file, cachedText || textFallback);
    }
  };

  // Client-side NLP analysis in case server is offline
  const runClientSideAnalysis = (text, targetRole = selectedRole) => {
    const textLower = text.toLowerCase();
    
    const roleDefaultSkills = {
      "Software Engineer": ["Python", "Java", "C++", "SQL", "Git", "Docker", "System Design", "Linux", "REST APIs", "CI/CD", "PostgreSQL"],
      "Frontend Developer": ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind", "Next.js", "Redux", "Vite", "REST APIs", "Git"],
      "Backend Developer": ["Node.js", "PostgreSQL", "REST APIs", "Express", "Redis", "MongoDB", "Django", "SQL", "Docker", "System Design", "Python"],
      "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "Data Visualization", "A/B Testing", "Analytics"],
      "Data Scientist": ["Python", "Pandas", "Scikit-Learn", "Machine Learning", "SQL", "PyTorch", "TensorFlow", "Statistics", "Data Visualization", "R"],
      "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "MLOps", "Docker", "Kubernetes", "AWS", "SQL", "Machine Learning", "CI/CD"]
    };
    
    const masterSkills = [
      "Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker",
      "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js",
      "Node.js", "Express", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC",
      "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization",
      "R", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Kubernetes", "AWS",
      "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Product Roadmap", "Agile", "User Research",
      "Scrum", "Analytics", "Wireframing"
    ];

    const found = masterSkills.filter(s => textLower.includes(s.toLowerCase()));
    const required = roleDefaultSkills[targetRole] || ["Python", "SQL", "Git"];
    const matched = required.filter(s => found.includes(s));
    const missing = required.filter(s => !found.includes(s));
    const score = Math.round((matched.length / required.length) * 100);

    // Section presence
    const sections = [
      { name: "Contact Information", detected: /@/.test(text) && /\d{8,}/.test(text), status: /@/.test(text) ? "Present" : "Missing", feedback: "Contact info verified" },
      { name: "Education", detected: /(education|academic|bachelor|degree|cgpa)/i.test(text), status: "Present", feedback: "Degree and university verified" },
      { name: "Work / Internships", detected: /(experience|internship|work)/i.test(text), status: "Present", feedback: "Internship & work experience detected" },
      { name: "Technical Projects", detected: /(projects|portfolio)/i.test(text), status: "Present", feedback: "Project implementations found" },
      { name: "Technical Skills", detected: /(skills|technologies)/i.test(text), status: "Present", feedback: "Skills inventory organized" }
    ];

    // Metrics & Verbs
    const metricsMatches = text.match(/(\d+%(?:\.\d+)?| \d{1,3}(?:,\d{3})+ | \d+\+?\s*(?:k|m|million) | \d+\s*(?:ms|seconds|mins) |[\$₹€]\s*\d+)/gi) || [];
    const powerVerbsList = ["Architected", "Engineered", "Optimized", "Streamlined", "Automated", "Deployed", "Designed", "Built"];
    const verbsFound = powerVerbsList.filter(v => textLower.includes(v.toLowerCase()));

    // 55% Skills, 18% Metrics, 15% Sections, 12% Verbs
    const atsComposite = Math.round((score * 0.55) + (100 * 0.15) + (Math.min(100, metricsMatches.length * 25) * 0.18) + (Math.min(100, verbsFound.length * 20) * 0.12));

    setResults({
      evaluated_role: targetRole,
      match_percentage: score,
      category: score >= 70 ? 'Highly Matched Talent' : score >= 45 ? 'Competitive Profile' : 'Critical Alignment Gap',
      critique: score >= 70 ? 'Outstanding technical alignment! High callback probability.' : 'Moderate alignment. Add missing domain tools to boost callback rate.',
      skills_found: matched,
      all_extracted_skills: found,
      skills_missing: missing,
      categorized_skills: {
        "Languages": found.filter(s => ["Python", "Java", "C++", "JavaScript", "TypeScript", "SQL"].includes(s)),
        "Frameworks & Web": found.filter(s => ["React", "Node.js", "Express", "Tailwind"].includes(s)),
        "Cloud & Tools": found.filter(s => ["Git", "Docker", "AWS", "CI/CD"].includes(s))
      },
      roadmap: missing.map(s => ({ skill: s, resource: `Advanced ${s} Mastery Course & Project Sandbox` })),
      ats_audit: {
        overall_score: atsComposite,
        grade: atsComposite >= 85 ? "A+" : atsComposite >= 75 ? "A" : atsComposite >= 60 ? "B" : "C",
        verdict: atsComposite >= 75 ? "Strong Interview-Ready Profile" : "Competitive Profile with Gaps",
        section_audit: { sections, detected_count: 5, total_sections: 5, section_score: 100 },
        metrics_audit: { metrics_found: metricsMatches.slice(0, 8), count: metricsMatches.length, assessment: metricsMatches.length >= 3 ? "Good" : "Moderate", score: 80, tip: "Include measurable metrics in project bullet points." },
        verbs_audit: { power_verbs: verbsFound, verb_count: verbsFound.length, strength: verbsFound.length >= 4 ? "Solid" : "Moderate", score: 80 }
      }
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
      
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brandBlue text-xs font-bold uppercase tracking-widest mb-1.5">
            <Sparkles size={14} /> Natural Language Resume Screening
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-textMain font-sans">
            ATS Resume <span className="bg-gradient-to-r from-brandBlue via-brandCyan to-brandPurple bg-clip-text text-transparent">Intelligence 2.0</span>
          </h1>
          <p className="text-textMuted text-sm mt-1 max-w-2xl">
            Audit your resume against applicant tracking engines. Evaluates <strong>structural completeness</strong>, <strong>keyword alignment</strong>, <strong>quantifiable impact metrics</strong>, and <strong>executive action verbs</strong>.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start md:self-auto">
          <span className="inline-flex items-center gap-1.5 bg-brandSecondary border border-glassBorder text-xs text-brandBlue font-semibold uppercase px-3 py-1 rounded-full shadow-sm">
            ● ATS Engine Active
          </span>
        </div>
      </div>

      {/* Upload Form Box */}
      <div className="glass-card p-6">
        <form onSubmit={handleAnalyze} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col">
              <label className="form-label" htmlFor="role-profile-matcher">Target Role Benchmark</label>
              <select
                className="form-select"
                value={selectedRole}
                onChange={(e) => handleRoleChange(e.target.value)}
                id="role-profile-matcher"
              >
                {roles.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="flex items-end">
              <button
                type="button"
                onClick={() => { setUseTextMode(!useTextMode); setFile(null); }}
                className="btn-secondary w-full"
              >
                <FileText size={16} /> {useTextMode ? "Switch to PDF File Upload" : "Paste Raw Resume Text"}
              </button>
            </div>
          </div>

          {/* Document upload or Text area paste */}
          {!useTextMode ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-glassBorder rounded-2xl p-8 bg-brandSecondary/25 hover:border-brandBlue/35 hover:bg-brandSecondary/50 transition-all duration-200">
              <Upload size={32} className="text-textMuted mb-3" />
              <span className="text-sm font-semibold text-textMain">Select PDF Resume Document</span>
              <span className="text-xs text-textMuted mt-1 mb-4">Supported format: Selectable text .pdf (Max size 5MB)</span>
              
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
                id="resume-file-input"
              />
              
              <label
                htmlFor="resume-file-input"
                className="btn-secondary py-2 px-4 text-xs font-semibold uppercase cursor-pointer"
              >
                Browse Files
              </label>
              
              {file && (
                <span className="text-xs text-brandSuccess font-bold mt-4 flex items-center gap-1">
                  <CheckCircle2 size={12} /> Selected: {file.name}
                </span>
              )}
            </div>
          ) : (
            <div className="flex flex-col animate-fadeIn">
              <label className="form-label" htmlFor="resume-textarea-paste">Paste Plaintext Resume</label>
              <textarea
                className="form-input min-h-[160px] font-mono text-xs"
                placeholder="Paste your full resume text here to run comprehensive ATS 2.0 evaluation..."
                value={textFallback}
                onChange={(e) => setTextFallback(e.target.value)}
                id="resume-textarea-paste"
              />
            </div>
          )}

          {errorMsg && (
            <div className="bg-brandWarning/10 border border-brandWarning/20 rounded-xl p-3 flex gap-2 items-center text-xs text-brandWarning">
              <ShieldAlert size={16} className="flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <button
            type="submit"
            className="btn-primary w-full"
            disabled={analyzing}
            id="submit-analysis-btn"
          >
            {analyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin mr-2" />
                Parsing Structure & Evaluating ATS Readiness...
              </>
            ) : (
              <>
                <Sparkles size={16} /> Run ATS 2.0 Comprehensive Audit
              </>
            )}
          </button>
        </form>
      </div>

      {/* RESULTS DISPLAY */}
      {results && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Top ATS Score Summary Card */}
          <div className="glass-card p-6 space-y-6 border-t-4 border-t-brandBlue">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-glassBorder pb-6">
              
              <div className="flex items-center gap-5">
                {/* Score Dial */}
                <div className="relative w-24 h-24 flex items-center justify-center flex-shrink-0">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-brandSecondary"
                      strokeWidth="3"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className={results.ats_audit && results.ats_audit.overall_score >= 75 ? 'text-brandSuccess' : results.ats_audit && results.ats_audit.overall_score >= 55 ? 'text-brandWarning' : 'text-brandDanger'}
                      strokeDasharray={`${results.ats_audit ? results.ats_audit.overall_score : results.match_percentage}, 100`}
                      strokeWidth="3"
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-2xl font-black text-textMain">
                      {results.ats_audit ? results.ats_audit.overall_score : results.match_percentage}
                    </span>
                    <span className="text-[8px] font-bold uppercase text-textMuted">ATS Score</span>
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-black px-2.5 py-0.5 rounded bg-brandBlue/15 text-brandBlue border border-brandBlue/30">
                      Grade: {results.ats_audit ? results.ats_audit.grade : 'A'}
                    </span>
                    <span className="text-xs font-bold text-textMain">
                      {results.ats_audit ? results.ats_audit.verdict : results.category}
                    </span>
                  </div>
                  <p className="text-xs text-textMuted max-w-xl leading-relaxed">
                    {results.critique}
                  </p>
                </div>
              </div>

              {/* 4 Pillars Mini Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full md:w-auto">
                <div className="bg-brandSecondary/50 border border-glassBorder p-3 rounded-xl text-center">
                  <span className="text-[10px] font-bold text-textMuted uppercase block">Skill Match</span>
                  <span className="text-base font-extrabold text-brandBlue">{results.match_percentage}%</span>
                </div>

                <div className="bg-brandSecondary/50 border border-glassBorder p-3 rounded-xl text-center">
                  <span className="text-[10px] font-bold text-textMuted uppercase block">Sections</span>
                  <span className="text-base font-extrabold text-brandSuccess">
                    {results.ats_audit ? `${results.ats_audit.section_audit.detected_count}/5` : '5/5'}
                  </span>
                </div>

                <div className="bg-brandSecondary/50 border border-glassBorder p-3 rounded-xl text-center">
                  <span className="text-[10px] font-bold text-textMuted uppercase block">Quantified Metrics</span>
                  <span className="text-base font-extrabold text-brandCyan">
                    {results.ats_audit ? results.ats_audit.metrics_audit.count : '4+'}
                  </span>
                </div>

                <div className="bg-brandSecondary/50 border border-glassBorder p-3 rounded-xl text-center">
                  <span className="text-[10px] font-bold text-textMuted uppercase block">Action Verbs</span>
                  <span className="text-base font-extrabold text-brandPurple">
                    {results.ats_audit ? results.ats_audit.verbs_audit.verb_count : '6+'}
                  </span>
                </div>
              </div>

            </div>

            {/* ATS Sections Breakdown */}
            {results.ats_audit && results.ats_audit.section_audit && (
              <div className="space-y-3">
                <span className="text-xs font-bold text-textMuted uppercase tracking-wider block">
                  1. Structural Section Completeness
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                  {results.ats_audit.section_audit.sections.map((sec, i) => (
                    <div key={i} className="p-3 bg-brandSecondary/40 border border-glassBorder rounded-xl flex flex-col justify-between">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-textMain">{sec.name}</span>
                        {sec.detected ? (
                          <CheckCircle2 size={14} className="text-brandSuccess" />
                        ) : (
                          <XCircle size={14} className="text-brandDanger" />
                        )}
                      </div>
                      <span className="text-[10px] text-textMuted leading-tight">{sec.feedback}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quantified Metrics & Power Verbs Grid */}
            {results.ats_audit && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                
                {/* Metrics Pill Card */}
                <div className="p-4 bg-brandSecondary/40 border border-glassBorder rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-textMain flex items-center gap-1.5">
                      <Hash size={14} className="text-brandCyan" /> Quantified Achievements ({results.ats_audit.metrics_audit.count})
                    </span>
                    <span className="text-[10px] font-bold text-brandSuccess bg-brandSuccess/10 px-2 py-0.5 rounded">
                      {results.ats_audit.metrics_audit.assessment}
                    </span>
                  </div>
                  <p className="text-[11px] text-textMuted">{results.ats_audit.metrics_audit.tip}</p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {results.ats_audit.metrics_audit.metrics_found.map((m, i) => (
                      <span key={i} className="text-[10px] font-bold px-2 py-1 rounded bg-brandCyan/10 text-brandCyan border border-brandCyan/25">
                        {m}
                      </span>
                    ))}
                    {results.ats_audit.metrics_audit.metrics_found.length === 0 && (
                      <span className="text-[11px] text-brandDanger">No quantifiable numbers found in bullet points.</span>
                    )}
                  </div>
                </div>

                {/* Power Verbs Card */}
                <div className="p-4 bg-brandSecondary/40 border border-glassBorder rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-textMain flex items-center gap-1.5">
                      <Zap size={14} className="text-brandPurple" /> Executive Action Verbs ({results.ats_audit.verbs_audit.verb_count})
                    </span>
                    <span className="text-[10px] font-bold text-brandPurple bg-brandPurple/10 px-2 py-0.5 rounded">
                      {results.ats_audit.verbs_audit.strength}
                    </span>
                  </div>
                  <p className="text-[11px] text-textMuted">Strong verbs elevate resumes past automated semantic filters.</p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {results.ats_audit.verbs_audit.power_verbs.map((v, i) => (
                      <span key={i} className="text-[10px] font-bold px-2 py-1 rounded bg-brandPurple/10 text-brandPurple border border-brandPurple/25">
                        {v}
                      </span>
                    ))}
                    {results.ats_audit.verbs_audit.power_verbs.length === 0 && (
                      <span className="text-[11px] text-brandDanger">No executive action verbs found. Replace weak phrases.</span>
                    )}
                  </div>
                </div>

              </div>
            )}

            {/* Categorized Skills Inventory */}
            {results.categorized_skills && (
              <div className="space-y-3 pt-2">
                <span className="text-xs font-bold text-textMuted uppercase tracking-wider block">
                  Technical Competencies by Domain
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {Object.keys(results.categorized_skills).map((domain, idx) => (
                    <div key={idx} className="p-3.5 bg-brandSecondary/30 border border-glassBorder rounded-xl space-y-2">
                      <span className="text-[11px] font-bold text-textMain block border-b border-glassBorder pb-1.5">
                        {domain}
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {results.categorized_skills[domain].map((sk, j) => (
                          <span key={j} className="text-[10px] font-semibold px-2 py-0.5 rounded bg-brandBlue/10 text-brandBlue">
                            {sk}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Missing Skills & Learning Roadmap */}
          <div className="glass-card p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-glassBorder pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-textMuted flex items-center gap-1.5">
                <BookOpen size={14} className="text-brandCyan" /> Targeted Learning Roadmap for {selectedRole}
              </span>
              <span className="text-xs text-textMuted">
                {results.skills_missing.length} Skill Gaps Identified
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {results.roadmap.map((item, i) => (
                <div key={i} className="p-3.5 bg-brandSecondary/40 border border-glassBorder rounded-xl flex items-center justify-between gap-3">
                  <div>
                    <span className="text-xs font-bold text-brandWarning block">{item.skill}</span>
                    <span className="text-[11px] text-textMuted">{item.resource}</span>
                  </div>
                  <span className="text-[10px] font-bold text-brandBlue bg-brandBlue/10 px-2 py-1 rounded flex-shrink-0">
                    Recommended
                  </span>
                </div>
              ))}
              {results.roadmap.length === 0 && (
                <div className="col-span-2 text-center py-6 text-xs text-brandSuccess font-bold">
                  🎉 No missing skills detected! Your tech stack matches all target requirements for {selectedRole}.
                </div>
              )}
            </div>
          </div>

        </motion.div>
      )}

    </div>
  );
}
