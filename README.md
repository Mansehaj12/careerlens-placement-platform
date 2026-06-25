# CareerLens: AI-Powered Job Market Intelligence & Placement Analytics Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-emerald.svg)](https://flask.palletsprojects.com/)
[![Tailwind CSS v3](https://img.shields.io/badge/Tailwind-v3-skyblue.svg)](https://tailwindcss.com/)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

**CareerLens** is a production-quality, end-to-end data engineering and predictive machine learning SaaS application. It analyzes global technology job postings, standardizes salary data, parses candidate resumes, and evaluates placement probabilities based on academic and project profiles.

Developed with modern clean architecture, CareerLens looks like a real-world startup product.

---

## 🌟 Core Product Features

### 1. Job Market Intelligence Dashboard
- **Dynamic Visualizations**: Uses Recharts to render salary areas by standard roles, skill demand lists, remote work distributions, and experience requirements.
- **Processed Jobs Browser**: Displays an interactive, filterable search table of cleaned records stored inside the SQLite relational database.
- **Pipeline Data Quality Report**: Displays **Before vs. After** data cleaning comparison metrics, highlighting duplicates dropped, missing fields resolved, and salary outliers filtered.

### 2. Machine Learning Salary Predictor
- **Ridge Regression Inference**: Estimates base salary levels in real-time, outputting range bounds based on the model's standard deviation (RMSE: ~$24,198).
- **Market Percentile Dial**: Calculates where the candidate sits in the market salary distribution.
- **ML Coefficient Importance**: Renders a bar chart representing the trained regression weights for each role, location, experience tier, and skill.

### 3. PDF Resume Skill Gap Analyzer
- **NLP PDF Parser**: Uses `pypdf` in the Flask backend to parse uploaded resume PDFs.
- **Weighted Skill Intersection**: Compares extracted tech keywords against required market keywords for the target role, outputting a weighted compatibility score.
- **Learning Roadmap**: Highlights missing skills and suggests specific online courses (Udemy/Coursera/Docker Labs) to bridge the gap.

### 4. Student Placement & What-If Simulator
- **Decision Tree Classification**: Fits a classifier on 5,000 student academic profiles to predict placement likelihood.
- **Real-Time Sliders**: Slide the CGPA bar, toggle internship counts, or add projects and certifications. The system calls the ML classifier in real-time to recalculate the placement probability dial.
- **Actionable Critique**: Details automated suggestions based on deficiencies (e.g. academic thresholds, project gaps).

---

## 📁 Repository Structure

```
├── Datasets/
│   ├── generate_dataset.py     # Messy simulation generator (52,000 jobs, 5,000 students)
│   ├── pipeline.py             # Pandas cleaning pipeline, outlier detection, quality reports
│   ├── raw_jobs.csv            # Intentionally messy generated CSV (git ignored)
│   ├── cleaned_jobs.csv        # Cleaned dataset ready for DB injection
│   ├── student_profiles.csv    # Student training records (git ignored)
│   └── data_quality.json       # JSON file comparing metrics before/after ETL
├── Models/
│   ├── train_models.py         # Trains Ridge Regressor and Decision Tree Classifier
│   ├── salary_model.joblib      # Serialized salary predictor weights
│   ├── salary_encoder.joblib    # Serialized categorical encoder
│   └── placement_model.joblib   # Serialized placement classifier model
├── Backend/
│   ├── app.py                  # Flask endpoints for stats, ML prediction & NLP PDF parsing
│   ├── database.py             # SQLite DB initializer & automatic seeder
│   ├── parser.py               # PDF resume text extraction and skill indexer
│   ├── requirements.txt        # Backend dependencies list
│   └── careerlens.db           # SQLite database file (created on startup)
├── Frontend/
│   ├── public/data/            # Loaded by React for client fallbacks
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx               # Header routing tabs
│   │   │   ├── MarketDashboard.jsx      # Analytics visualizations & ETL metrics
│   │   │   ├── SalaryPredictor.jsx      # Predictor calculator & coefficient charts
│   │   │   ├── ResumeMatcher.jsx        # PDF uploader, score match, & roadmap
│   │   │   └── PlacementAnalytics.jsx   # Placement probability & What-If ML simulator
│   │   ├── App.jsx                      # Page layout routing
│   │   ├── index.css                    # Tailwind CSS configuration imports
│   │   └── main.jsx                     # Render mount
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
├── Documentation/
│   └── DEPLOYMENT.md           # Production deployment steps (Vercel, Render, PostgreSQL)
└── README.md
```

---

## 🚀 Local Installation & Setup

### 1. Generate Datasets & Clean
Execute the simulation generator and ETL pipeline to generate raw datasets and clean standard CSVs:
```bash
# Generate 52,000 jobs & 5,000 student records
python Datasets/generate_dataset.py

# Clean duplicates, impute salaries, check outliers
python Datasets/pipeline.py
```

### 2. Train the Machine Learning Models
Fit the Ridge regression and Decision Tree models and serialize them:
```bash
# Train ML predictors and serialize models
python Models/train_models.py
```
*This compiles stats, weights, and model files, saving them to `Models/` and copying JSON configs into `Frontend/public/data/`.*

### 3. Run the Flask REST API Server
Start the Flask web server. On startup, it automatically runs the database initializer (`Backend/database.py`), creates the database tables, and seeds them with your cleaned jobs and student records:
```bash
# Install backend requirements
pip install -r Backend/requirements.txt

# Start the server (runs on http://127.0.0.1:5000)
python Backend/app.py
```

### 4. Run the React Frontend
Open a new terminal, navigate to the frontend folder, install packages, and spin up the Vite development server:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🔍 Code Walkthrough & Design Decisions

### 1. Hybrid Client-Server Architecture
To guarantee that your resume website can be previewed even if a live server is not hosted, the React frontend is written with **Dynamic Fallback Handlers**. If the Flask API server is offline, the React app automatically catches the network error, toggles a fallback state, and runs predictions/simulations client-side using static JSON datasets and pre-coded logit equations:
```javascript
// Fallback client simulation if Flask backend is offline
const executeClientSimulation = () => {
  const logit = -7.5 + (0.95 * cgpa) + (1.6 * internships) + (0.75 * projects) + (0.5 * certifications) + (0.1 * skillsCount);
  const prob = 1 / (1 + Math.exp(-logit));
  const score = Math.round(prob * 100);
  
  setResults({
    placement_probability: prob,
    employability_score: score,
    suggestions: suggestions
  });
};
```
This shows recruiters that you can design resilient systems that handle service disruptions gracefully.

### 2. Multi-hot Vector Coding for Text Processing
To predict salaries, we represent unstructured skills by training a Ridge model on multi-hot vectors mapping the presence of 50 technical keywords. The Flask server replicates this preprocessing vectorization on inputs:
```python
# Multi-hot encode incoming skills array
skills_dummies = pd.DataFrame(0, index=[0], columns=parser.ALL_SKILLS)
for s in skills:
    if s in parser.ALL_SKILLS:
        skills_dummies.loc[0, s] = 1
        
# Concatenate categorical one-hot vectors and predict
X_pred = pd.concat([cat_encoded_df, skills_dummies], axis=1)
predicted = salary_model.predict(X_pred)[0]
```
This demonstrates the ability to translate conceptual ML math into clean production APIs.
