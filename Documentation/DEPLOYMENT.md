# CareerLens: Production Deployment Guide

This guide details the steps to deploy **CareerLens** (React frontend + Python Flask backend + Database) to cloud hosting environments (Vercel, Render, Railway) and scale the database from SQLite to PostgreSQL.

---

## 💻 Frontend Deployment (React + Vite)

You can host the React frontend on **Vercel** or **Netlify** for free.

### Setup Steps:
1. Push your repository to GitHub.
2. Link your GitHub account to [Vercel](https://vercel.com) or [Netlify](https://netlify.com).
3. Import the repository and set the following parameters:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Set the Frontend environment variable if you have a running Python server:
   - Set up API base URL mappings in your fetch calls (e.g. mapping `http://127.0.0.1:5000` to your live Render backend URL).
5. Click **Deploy**.

---

## 🐍 Backend Deployment (Flask + ML Models)

Deploy the Flask API on **Render** (Free tier Web Service) or **Railway**.

### Setup Steps (Render):
1. Create a new **Web Service** on Render and connect your GitHub repository.
2. Configure the following project parameters:
   - **Root Directory**: `Backend` (or keep root and use start scripts)
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (ensure `gunicorn` is in your `requirements.txt` list)
3. Set the following environment variables in the Render settings panel:
   - `PYTHON_VERSION`: `3.12.9`
   - `FLASK_ENV`: `production`
   - `FLASK_APP`: `app.py`
4. Click **Deploy**.

---

## 🗄️ Database Scaling: SQLite to PostgreSQL

By default, CareerLens runs on **SQLite** (`Backend/careerlens.db`) which is zero-setup. However, for a production environment, migrating to **PostgreSQL** is highly recommended.

### Step 1: Create a PostgreSQL Instance
Provision a free database instance on **Supabase**, **Neon**, or **Render PostgreSQL**.

### Step 2: Configure Backend Connection String
In the Flask app, configure the database URL. To map this seamlessly:
1. In your `Backend/` folder, create a `.env` file (ensure it is Git ignored):
   ```env
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   ```
2. Update `Backend/database.py` to dynamically load the connection string:
   ```python
   import os
   from sqlalchemy import create_engine
   
   db_url = os.environ.get("DATABASE_URL", "sqlite:///Backend/careerlens.db")
   engine = create_engine(db_url)
   ```

### Step 3: Run Database Migrations
On startup, `database.init_db()` will automatically check the connection engine and compile the tables (`jobs` and `students`) in PostgreSQL, seeding them if they are empty.

---

## 📝 Environment Variables Checklist

Ensure these variables are set in production:

| Variable Name | Description | Example / Recommended |
| :--- | :--- | :--- |
| `FLASK_ENV` | Mode of operation | `production` |
| `DATABASE_URL` | DB Connection String | `postgresql://user:pass@host:5432/db` |
| `PORT` | Web Server Port | `5000` (Render handles this automatically) |
