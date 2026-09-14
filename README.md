# CareerLens 2.0: AI-Powered Tech Market Intelligence & Placement Analytics Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-emerald.svg)](https://flask.palletsprojects.com/)
[![Tailwind CSS v3](https://img.shields.io/badge/Tailwind-v3-skyblue.svg)](https://tailwindcss.com/)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

### 🌐 Live Deployment
* **Live Web App (React + Vite):** [https://careerlens-placement-platform.vercel.app/](https://careerlens-placement-platform.vercel.app/)
* **Production API (Flask):** [https://sehaj1104.pythonanywhere.com/](https://sehaj1104.pythonanywhere.com/)
* **Version Evolution Guide:** [PROJECT_EVOLUTION_V1_TO_V2.md](PROJECT_EVOLUTION_V1_TO_V2.md)

**CareerLens 2.0** is an enterprise-grade data engineering and predictive machine learning SaaS application. It aggregates technology job market data, standardizes compensation figures, evaluates candidate resumes with a role-aware multi-dimensional ATS engine, models placement probabilities, and provides cross-validated model benchmarking.

Built with clean architecture, modern glassmorphism, and fault-tolerant client fallbacks.

---

## 🌟 Core Product Modules

### 1. Job Market Intelligence Dashboard (`/`)
- **Dynamic Visualizations**: Utilizes Recharts to render market distributions across standard roles, skill demand hierarchies, remote work prevalence, and experience tiers.
- **Processed Jobs Explorer**: Filterable, searchable table of cleaned market records backed by SQLite/relational storage.
- **Pipeline Data Quality Audit**: Before vs. After ETL metrics detailing duplicate elimination, null-value imputation, and outlier filtering.

### 2. Machine Learning Salary Predictor (`/predict-salary`)
- **Ridge Regularization ($\alpha=50$)**: Employs an $L_2$-penalized regression model cross-validated across 5 folds to stabilize feature weights and prevent collinear coefficient distortion.
- **Empirical Uncertainty Quantification**: Provides realistic salary ranges based on 5-Fold CV MAE ($\pm\text{₹}4.35\text{L}$) and percentile bounds.
- **Market Standing Percentile**: Visualizes where a candidate's profile ranks relative to the broader engineering compensation distribution.
- **Feature Weight Interpretability**: Interactive chart illustrating the relative influence of roles, locations, experience tiers, and individual technical skills.

### 3. Resume ATS & Gap Analyzer (`/resume-analyzer`)
- **Multi-Dimensional Role-Specific ATS Engine**:
  $$\text{ATS Score} = (0.55 \times \text{Domain Skills}) + (0.18 \times \text{Measurable Metrics}) + (0.15 \times \text{Standard Sections}) + (0.12 \times \text{Action Verbs})$$
- **Role Taxonomy with Synonyms**: Supports distinct requirements for Software Engineers, Frontend Developers, Backend Developers, Data Scientists, and ML Engineers.
- **Live Dropdown Re-Evaluation**: Upload once—switching target roles immediately recalculates ATS compatibility and skill gaps on the fly without re-parsing.
- **Measurable Impact Extraction**: Automatically detects quantifiable accomplishments (metrics, percentages, performance benchmarks).
- **Targeted Learning Roadmap**: Identifies missing core technologies and recommends targeted resources to bridge domain gaps.

### 4. Student Placement What-If Simulator (`/placement`)
- **Calibrated Starting Baseline**: Initialized to a realistic starting position (**5.0 CGPA, 0 Skills, 0 Internships, 0 Projects** $\to$ baseline **~35% risk tier**).
- **Real-Time Interactive Sliders**: Dynamically evaluate marginal gains from boosting CGPA, completing internships, publishing projects, or earning certifications.
- **Actionable Critique**: Automated diagnostic feedback identifying high-leverage areas for profile improvement.

### 5. ML Model Benchmarks (`/benchmarks`)
- **Comparative Algorithm Matrix**: Side-by-side performance comparison of Logistic Regression, Random Forest, and Gradient Boosting.
- **Production Metrics**: Evaluates Accuracy, ROC-AUC, Precision, Recall, F1 Score, and Cross-Validation Variance.

### 6. Glassmorphic 2.0 Design System
- **Atmospheric Aurora Lighting**: Multi-stop ambient glow layer providing subtle depth.
- **Glassmorphism**: Translucent cards with `backdrop-filter: blur(14px)` and specular top borders.
- **Dynamic Dark/Light Adaptation**: Live `MutationObserver` synchronization adapting Recharts palettes, tooltip colors, and typography contrasts seamlessly.

---

## 📁 Repository Structure

```
├── Datasets/
│   ├── generate_dataset.py       # Simulation generator (52,000 jobs, 5,000 students)
│   ├── pipeline.py               # Pandas cleaning pipeline, outlier detection, quality reports
│   ├── raw_jobs.csv              # Raw simulated CSV (git ignored)
│   ├── cleaned_jobs.csv          # Cleaned dataset ready for DB injection
│   ├── student_profiles.csv      # Student training records (git ignored)
│   └── data_quality.json         # ETL before/after validation metrics
├── Models/
│   ├── train_models.py           # Trains Ridge Regressor & Placement Classifiers with 5-Fold CV
│   ├── salary_model.joblib        # Serialized Ridge salary predictor
│   ├── salary_encoder.joblib      # Serialized categorical encoder
│   └── placement_model.joblib     # Serialized placement classifier
├── Backend/
│   ├── app.py                    # Flask REST API endpoints (prediction, stats, PDF parser)
│   ├── database.py               # SQLite DB initializer & automatic seeder
│   ├── parser.py                 # Multi-dimensional ATS engine & NLP text extraction
│   ├── requirements.txt          # Python dependencies
│   └── careerlens.db             # Local SQLite database
├── frontend/
│   ├── public/data/              # Model statistics, benchmarks, and fallback datasets
│   │   ├── model_benchmarks.json
│   │   ├── placement_model_stats.json
│   │   └── salary_model_stats.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx             # Header navigation with theme toggle
│   │   │   ├── MarketDashboard.jsx    # Analytics visualizations & ETL audit
│   │   │   ├── SalaryPredictor.jsx    # Ridge salary estimator & weights
│   │   │   ├── ResumeMatcher.jsx      # Multi-dimensional ATS resume analyzer
│   │   │   ├── PlacementAnalytics.jsx # Calibrated What-If simulator
│   │   │   └── ModelBenchmarks.jsx    # Comparative algorithm evaluation
│   │   ├── App.jsx                    # Root layout with aurora ambient lighting
│   │   ├── config.js                  # Dynamic API base URL configuration
│   │   ├── index.css                  # Tailwind styles & glassmorphic system
│   │   └── main.jsx                   # Application entry point
│   ├── vercel.json                    # Vercel SPA route rewrite rules
│   ├── package.json
│   └── vite.config.js
├── vercel.json                        # Root Vercel SPA rewrite configuration
├── PROJECT_EVOLUTION_V1_TO_V2.md      # Comprehensive v1.0 -> v2.0 transformation report
└── README.md
```

---

## 🚀 Local Installation & Setup

### 1. Generate Datasets & Run ETL Pipeline
```bash
# Generate simulation records
python Datasets/generate_dataset.py

# Execute cleaning pipeline and generate data quality metrics
python Datasets/pipeline.py
```

### 2. Train & Benchmark Machine Learning Models
```bash
# Fit Ridge regression and placement classifiers with cross-validation
python Models/train_models.py
```
*This updates model files in `Models/` and exports benchmark JSONs into `frontend/public/data/`.*

### 3. Launch Flask Backend Server
```bash
# Install dependencies
pip install -r Backend/requirements.txt

# Start backend server (runs on http://127.0.0.1:5000)
python Backend/app.py
```

### 4. Launch React Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🛡️ Architecture & Resilience

### Hybrid Client-Server Failover
The frontend features **Dynamic Fallback Handlers**. If the remote Flask API server is unreachable, the application gracefully falls back to client-side mathematical simulation using cached model stats and logit equations, ensuring zero user disruption during outages.

### Single Page Application (SPA) Routing on Vercel
Configured with wildcard rewrites in `vercel.json` (`/(.*) -> /index.html`), ensuring deep links and browser refreshes across all subroutes (`/predict-salary`, `/placement`, `/resume-analyzer`, `/benchmarks`) load seamlessly without `404: NOT_FOUND` errors.
