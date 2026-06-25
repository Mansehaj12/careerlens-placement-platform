import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle2, AlertTriangle, ArrowRight, BookOpen, ShieldAlert, Sparkles, Check, Plus } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ResumeMatcher() {
  const [selectedRole, setSelectedRole] = useState('Software Engineer');
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [textFallback, setTextFallback] = useState('');
  const [useTextMode, setUseTextMode] = useState(false);

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
      setErrorMsg('');
    }
  };

  const handleAnalyze = (e) => {
    if (e) e.preventDefault();
    setErrorMsg('');
    setResults(null);

    if (!file && (!useTextMode || !textFallback.trim())) {
      setErrorMsg('Please select a PDF file or paste your resume text first.');
      return;
    }

    setAnalyzing(true);

    const formData = new FormData();
    formData.append('role', selectedRole);
    if (useTextMode) {
      setTimeout(() => {
        runClientSideAnalysis(textFallback);
        setAnalyzing(false);
      }, 1000);
      return;
    }

    formData.append('file', file);

    fetch('http://127.0.0.1:5000/api/analyze/resume', {
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
        setAnalyzing(false);
      })
      .catch((err) => {
        console.warn("PDF Upload API failed, attempting client fallback via text paste...", err);
        setErrorMsg('Flask server offline or PDF read error. Toggled Text Paste fallback mode.');
        setUseTextMode(true);
        setAnalyzing(false);
      });
  };

  // Client-side NLP analysis in case server is offline
  const runClientSideAnalysis = (text) => {
    const textLower = text.toLowerCase();
    
    const roleDefaultSkills = {
      "Software Engineer": ["Python", "Java", "Git", "SQL", "Docker", "C++", "System Design"],
      "Frontend Developer": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Tailwind", "Next.js"],
      "Backend Developer": ["Node.js", "Express", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC"],
      "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing"],
      "Data Scientist": ["Python", "SQL", "Pandas", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "Statistics"],
      "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "MLOps", "Docker", "Kubernetes", "AWS"]
    };
    
    const requiredSkills = roleDefaultSkills[selectedRole] || ["Python", "SQL"];
    const found = [];
    
    const required_skills_keywords = {
      "python": ["python"],
      "java": ["java"],
      "c++": ["c++", "cpp"],
      "go": ["golang", "go lang", "go"],
      "system design": ["system design", "microservices", "architecture"],
      "git": ["git", "github", "gitlab"],
      "sql": ["sql", "mysql", "sqlite", "oracle"],
      "docker": ["docker", "containerization"],
      "javascript": ["javascript", "js"],
      "typescript": ["typescript", "ts"],
      "react": ["react", "reactjs", "react.js"],
      "html5": ["html5", "html"],
      "css3": ["css3", "css"],
      "redux": ["redux", "redux-toolkit"],
      "tailwind": ["tailwind", "tailwindcss"],
      "next.js": ["nextjs", "next.js", "next"],
      "node.js": ["nodejs", "node.js", "node"],
      "express": ["express", "expressjs"],
      "postgresql": ["postgresql", "postgres"],
      "mongodb": ["mongodb", "mongo"],
      "redis": ["redis"],
      "rest apis": ["rest api", "restful", "apis", "rest apis"],
      "grpc": ["grpc"],
      "excel": ["excel", "xlsx", "spreadsheets"],
      "tableau": ["tableau"],
      "power bi": ["power bi", "powerbi"],
      "pandas": ["pandas"],
      "statistics": ["statistics", "statistical", "probability"],
      "a/b testing": ["a/b testing", "ab testing", "hypothesis testing"],
      "data visualization": ["data visualization", "charts", "plots"],
      "r": ["r lang", "r programming"],
      "scikit-learn": ["scikit-learn", "sklearn"],
      "tensorflow": ["tensorflow", "tf"],
      "pytorch": ["pytorch"],
      "machine learning": ["machine learning", "ml"],
      "mlops": ["mlops", "model deployment"],
      "kubernetes": ["kubernetes", "k8s"],
      "aws": ["aws", "amazon web services", "cloud"],
      "ci/cd": ["ci/cd", "ci-cd", "jenkins", "github actions"],
      "terraform": ["terraform"],
      "linux": ["linux", "unix"],
      "bash": ["bash", "shell scripting"],
      "jenkins": ["jenkins"],
      "product roadmap": ["product roadmap", "roadmap"],
      "agile": ["agile", "scrum", "sprints"],
      "user research": ["user research", "ux research"],
      "scrum": ["scrum"],
      "analytics": ["analytics", "product analytics"],
      "wireframing": ["wireframing", "figma", "wireframe"]
    };

    requiredSkills.forEach(skill => {
      const aliases = required_skills_keywords[skill.toLowerCase()] || [skill.toLowerCase()];
      const matches = aliases.some(alias => {
        let pattern = '\\b' + alias.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&') + '\\b';
        if (['c++', 'next.js', 'node.js', 'ci/cd', 'a/b testing', 'html5', 'css3'].includes(alias)) {
          pattern = alias.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        }
        return new RegExp(pattern).test(textLower);
      });
      if (matches) {
        found.push(skill);
      }
    });

    const missing = requiredSkills.filter(s => !found.includes(s));
    const score = requiredSkills.length > 0 ? Math.round((found.length / requiredSkills.length) * 100) : 0;

    const courseRecommendations = {
      "Python": "Python for Data Science (Kaggle / Coursera)",
      "SQL": "Complete SQL Bootcamp (Udemy / LeetCode Database)",
      "React": "React Documentation Tutorials & FreeCodeCamp Full Course",
      "AWS": "AWS Certified Cloud Practitioner Pathway",
      "Docker": "Docker & Kubernetes Containerization Fundamentals (Docker Labs)",
      "Tableau": "Data Visualization Specialist Course (Tableau eLearning)",
      "Power BI": "Microsoft PL-300 Business Analyst Certification Pathway",
      "Machine Learning": "Introduction to Machine Learning (Andrew Ng on Coursera)",
      "System Design": "System Design Primer & Designing Data-Intensive Applications",
      "CI/CD": "DevOps Foundations: Continuous Integration & Deployment (GitHub Actions)",
      "Kubernetes": "Certified Kubernetes Administrator (CKA) Training"
    };

    const roadmap = missing.map(s => ({
      skill: s,
      resource: courseRecommendations[s] || `Advanced ${s} Guides & Project Building`
    }));

    let critique = '';
    let category = '';
    if (score < 35) {
      category = 'Critical Alignment Gap';
      critique = 'Your resume shows a strong mismatch for this role. You are missing key technological foundations. We recommend building 2-3 targeted projects using the missing technologies and documenting them on GitHub before applying.';
    } else if (score >= 35 && score < 70) {
      category = 'Competitive Profile';
      critique = 'You possess solid core skills, but you are missing several secondary tools that distinguish premium candidates. Adding minor keyword modifications and highlighting hands-on experiences with containerization or SQL querying will boost screening rates.';
    } else {
      category = 'Highly Matched Talent';
      critique = 'Excellent skill alignment! Your resume effectively matches market demand. To stand out even further to human recruiters, focus on showcasing quantified achievements (e.g., "reduced query times by 40%") rather than just listing technologies.';
    }

    setResults({
      match_percentage: score,
      category,
      critique,
      skills_found: found,
      skills_missing: missing,
      roadmap
    });
  };

  const loadSampleResume = () => {
    const samples = {
      "Data Analyst": "Resume:\nJohn Doe - Junior Data Analyst\nSkills: SQL, Python (Pandas, Numpy), Microsoft Excel, Tableau dashboards, descriptive statistics, and A/B Testing.\nSummary: Experienced in data query creation, visualization reports, and business analysis metrics.",
      "Software Engineer": "Resume:\nJane Smith - Associate Software Engineer\nSkills: Java, C++, Python, Git version control, SQL databases, Docker containers, systems design.\nSummary: Designed scalable server APIs, managed backend integrations, and set up source control pipelines.",
      "Data Scientist": "Resume:\nSarah Lee - Data Scientist\nSkills: Python, SQL databases, Pandas, NumPy, Scikit-Learn modeling, machine learning, deep learning with PyTorch, predictive statistics.\nSummary: Trained statistical regressors, deployed predictive analytics models, and conducted data exploration."
    };
    setTextFallback(samples[selectedRole] || "Resume:\nI have skills in Python and Git...");
    setUseTextMode(true);
    setErrorMsg('');
  };

  // Run automatically if profile selected matches pre-set samples
  const selectPresetProfile = (presetRole, presetText) => {
    setSelectedRole(presetRole);
    setTextFallback(presetText);
    setUseTextMode(true);
    setErrorMsg('');
    
    // Trigger analysis in next tick once state matches
    setTimeout(() => {
      setAnalyzing(true);
      setTimeout(() => {
        runClientSideAnalysis(presetText);
        setAnalyzing(false);
      }, 700);
    }, 50);
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      
      {/* Title */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-textMain font-sans">Resume Gap Analyzer</h1>
        <p className="text-textMuted text-sm mt-1.5 font-normal">
          Upload your resume in PDF format to parse technology keywords and calculate compatibility against targeted market roles.
        </p>
      </div>

      <div className="space-y-6">
        
        {/* Preset Sample Profiles Selector (Handcrafted visual dashboard feel) */}
        <div className="glass-card p-6">
          <span className="form-label mb-3">Load Demo Profiles (Instant Mock Evaluation)</span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              onClick={() => selectPresetProfile(
                "Software Engineer",
                "Resume:\nMansehaj Preet Singh\nSkills: C++, Java, Python, Git version control, SQL, Docker containerization, and System Design primer.\nSummary: Engineering sophomore building high-performance backend pipelines."
              )}
              className="p-3 text-left rounded-xl border border-glassBorder bg-brandSecondary hover:border-brandBlue/40 hover:bg-brandBlue/5 transition-all duration-200 cursor-pointer flex flex-col justify-between"
            >
              <span className="text-xs font-bold text-textMain">Software Engineer</span>
              <span className="text-[10px] text-textMuted mt-1 block">Includes Docker, System Design, C++, Git</span>
            </button>
            <button
              onClick={() => selectPresetProfile(
                "Data Analyst",
                "Resume:\nJohn Doe - Junior Analyst\nSkills: SQL queries, Microsoft Excel spreadsheets, Tableau dashboard reporting, A/B Testing metrics, statistics.\nSummary: Analyst presenting metrics to key stakeholders."
              )}
              className="p-3 text-left rounded-xl border border-glassBorder bg-brandSecondary hover:border-brandBlue/40 hover:bg-brandBlue/5 transition-all duration-200 cursor-pointer flex flex-col justify-between"
            >
              <span className="text-xs font-bold text-textMain">Data Analyst</span>
              <span className="text-[10px] text-textMuted mt-1 block">Includes SQL, Tableau, Statistics, A/B Testing</span>
            </button>
            <button
              onClick={() => selectPresetProfile(
                "Data Scientist",
                "Resume:\nSarah Lee\nSkills: Python programming, Pandas modeling, NumPy data exploration, Scikit-Learn libraries, Machine Learning algorithms.\nSummary: Researcher fitting regression models and clustering structures."
              )}
              className="p-3 text-left rounded-xl border border-glassBorder bg-brandSecondary hover:border-brandBlue/40 hover:bg-brandBlue/5 transition-all duration-200 cursor-pointer flex flex-col justify-between"
            >
              <span className="text-xs font-bold text-textMain">Data Scientist</span>
              <span className="text-[10px] text-textMuted mt-1 block">Includes Python, ML, Pandas, Scikit-Learn</span>
            </button>
          </div>
        </div>

        {/* Configuration Box */}
        <div className="glass-card p-6">
          <form onSubmit={handleAnalyze} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex flex-col">
                <label className="form-label" htmlFor="role-profile-matcher">Target Career Profile</label>
                <select
                  className="form-select"
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  id="role-profile-matcher"
                >
                  {roles.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={loadSampleResume}
                  className="btn-secondary w-full"
                  id="load-sample-resume-btn"
                >
                  <FileText size={16} /> Paste Custom Text Fallback
                </button>
              </div>
            </div>

            {/* Document upload or Text area paste */}
            {!useTextMode ? (
              <div className="flex flex-col items-center justify-center border-2 border-dashed border-glassBorder rounded-2xl p-8 bg-brandSecondary/25 hover:border-brandBlue/35 hover:bg-brandSecondary/50 transition-all duration-200">
                <Upload size={32} className="text-textMuted mb-3" />
                <span className="text-sm font-semibold text-textMain">Select PDF Resume File</span>
                <span className="text-xs text-textMuted mt-1 mb-4">Supported formats: .pdf (Max size 5MB)</span>
                
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
                <label className="form-label" htmlFor="resume-textarea-paste">Paste Resume Text</label>
                <textarea
                  className="form-input min-h-[160px] font-mono text-xs"
                  placeholder="Paste your raw resume text here to evaluate keywords..."
                  value={textFallback}
                  onChange={(e) => setTextFallback(e.target.value)}
                  id="resume-textarea-paste"
                />
                <button
                  type="button"
                  onClick={() => { setUseTextMode(false); setFile(null); }}
                  className="text-brandBlue text-xs font-bold mt-2 self-end hover:underline cursor-pointer"
                  id="toggle-pdf-upload"
                >
                  ← Switch back to PDF Upload
                </button>
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
                  Analyzing Resume Structures...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Run Compatibility Engine
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results Card with Framer Motion */}
        {results && (
          <motion.div 
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className={`glass-card p-6 grid grid-cols-1 md:grid-cols-12 gap-8 border-t-4 ${
              results.match_percentage >= 70 
                ? 'border-t-brandSuccess' 
                : results.match_percentage >= 35 
                ? 'border-t-brandWarning' 
                : 'border-t-brandDanger'
            }`}
          >
            
            {/* Left section: Score & Critique */}
            <div className="md:col-span-6 space-y-6">
              
              <div className="flex items-center gap-4">
                {/* Radial Score Gauge */}
                <div className="relative w-20 h-20 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-brandSecondary"
                      strokeWidth="2.5"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className={
                        results.match_percentage >= 70 
                          ? 'text-brandSuccess' 
                          : results.match_percentage >= 35 
                          ? 'text-brandWarning' 
                          : 'text-brandDanger'
                      }
                      strokeDasharray={`${results.match_percentage}, 100`}
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <span className="absolute text-lg font-extrabold text-textMain">{results.match_percentage}%</span>
                </div>
                
                <div>
                  <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                    results.match_percentage >= 70 
                      ? 'bg-brandSuccess/10 text-brandSuccess border-brandSuccess/20' 
                      : results.match_percentage >= 35 
                      ? 'bg-brandWarning/10 text-brandWarning border-brandWarning/20' 
                      : 'bg-brandDanger/10 text-brandDanger border-brandDanger/20'
                  }`}>
                    {results.category}
                  </span>
                  <h4 className="text-sm font-bold text-textMain mt-1.5 font-sans">Role Compatibility Matrix</h4>
                </div>
              </div>

              {/* Critique critique */}
              <div className="bg-brandSecondary border border-glassBorder rounded-xl p-4 flex gap-3 items-start text-xs leading-relaxed">
                {results.match_percentage >= 70 ? (
                  <CheckCircle2 size={18} className="text-brandSuccess mt-0.5 flex-shrink-0" />
                ) : (
                  <AlertTriangle size={18} className={`mt-0.5 flex-shrink-0 ${results.match_percentage >= 35 ? 'text-brandWarning' : 'text-brandDanger'}`} />
                )}
                <div>
                  <h5 className="font-bold text-textMain mb-0.5">Resume Alignment Audit</h5>
                  <p className="text-textMuted leading-relaxed">{results.critique}</p>
                </div>
              </div>

              {/* Matched tags */}
              <div>
                <h5 className="form-label text-[10px]">Keywords Identified ({results.skills_found.length})</h5>
                <div className="flex flex-wrap gap-1.5">
                  {results.skills_found.map(skill => (
                    <span key={skill} className="bg-brandSuccess/10 text-brandSuccess border border-brandSuccess/15 text-[10px] font-semibold px-2.5 py-1 rounded-lg flex items-center gap-1">
                      <Check size={10} className="text-brandSuccess" /> {skill}
                    </span>
                  ))}
                  {results.skills_found.length === 0 && (
                    <span className="text-xs text-textMuted italic">No keywords matched.</span>
                  )}
                </div>
              </div>

            </div>

            {/* Right section: Missing & roadmap */}
            <div className="md:col-span-6 border-t md:border-t-0 md:border-l border-glassBorder pt-6 md:pt-0 md:pl-8 space-y-6">
              <h4 className="text-sm font-bold text-textMain flex items-center gap-2 border-b border-glassBorder pb-3">
                <BookOpen size={16} className="text-brandCyan" /> Skill Gap Curations
              </h4>
              <p className="text-textMuted text-xs leading-normal font-sans">
                We recommend targeted study pathways to cover outstanding screening keywords:
              </p>

              <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
                {results.roadmap.map(item => (
                  <div key={item.skill} className="bg-brandSecondary/60 border border-glassBorder rounded-xl p-3.5 text-xs flex flex-col gap-1.5">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-brandDanger flex items-center gap-1">
                        <Plus size={12} className="text-brandDanger rotate-45" /> {item.skill}
                      </span>
                      <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-brandDanger/10 text-brandDanger border border-brandDanger/15 rounded">Pending Gap</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-textMuted font-sans">
                      <ArrowRight size={10} className="flex-shrink-0 text-textMuted" />
                      <span>{item.resource}</span>
                    </div>
                  </div>
                ))}
                {results.roadmap.length === 0 && (
                  <div className="text-center py-6 text-brandSuccess font-bold text-sm flex flex-col items-center gap-2">
                    <CheckCircle2 size={24} />
                    <span>Profile has 100% keyword alignment! Ready to apply.</span>
                  </div>
                )}
              </div>
            </div>

          </motion.div>
        )}

      </div>

    </div>
  );
}
