import sqlite3
import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env if present
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # Fallback to standard search

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "Backend", "careerlens.db")
CLEANED_JOBS_CSV = os.path.join(BASE_DIR, "Datasets", "cleaned_jobs.csv")
STUDENTS_CSV = os.path.join(BASE_DIR, "Datasets", "student_profiles.csv")

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        import psycopg2
        from psycopg2.extras import DictCursor
        conn = psycopg2.connect(db_url, cursor_factory=DictCursor)
        return conn, "postgres"
    else:
        # Resolve DB path relative to project root if DB_PATH doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def check_connection():
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False

def init_db():
    print("Initializing Database...")
    try:
        conn, db_type = get_db_connection()
        print(f"Connected successfully to {db_type} database.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    cursor = conn.cursor()
    
    # Use appropriate syntax based on database type
    pk_syntax = "SERIAL PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    param_char = "%s" if db_type == "postgres" else "?"
    
    # 1. Create Jobs Table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS jobs (
            id {pk_syntax},
            title TEXT,
            company TEXT,
            location TEXT,
            salary_min REAL,
            salary_max REAL,
            salary_avg REAL,
            experience TEXT,
            skills TEXT,
            industry TEXT,
            employment_type TEXT,
            remote_status TEXT,
            posting_date TEXT
        )
    """)
    
    # 2. Create Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            cgpa REAL,
            skills_count INTEGER,
            internships INTEGER,
            projects INTEGER,
            certifications INTEGER,
            placed INTEGER
        )
    """)
    
    conn.commit()
    
    # 3. Seed Jobs if empty
    cursor.execute("SELECT COUNT(*) FROM jobs")
    if cursor.fetchone()[0] == 0:
        print("Seeding jobs table from cleaned_jobs.csv...")
        if os.path.exists(CLEANED_JOBS_CSV):
            with open(CLEANED_JOBS_CSV, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                jobs_to_insert = []
                for row in reader:
                    # Convert types safely
                    try:
                        salary_min = float(row.get("salary_min", 0))
                        salary_max = float(row.get("salary_max", 0))
                        salary_avg = float(row.get("salary_avg", 0))
                    except ValueError:
                        salary_min = salary_max = salary_avg = 0.0
                        
                    jobs_to_insert.append((
                        row.get("standard_title", row.get("title")),
                        row.get("company"),
                        row.get("clean_location", row.get("location")),
                        salary_min,
                        salary_max,
                        salary_avg,
                        row.get("clean_experience", row.get("experience")),
                        row.get("clean_skills_str", row.get("skills")),
                        row.get("industry"),
                        row.get("employment_type"),
                        row.get("clean_remote", row.get("remote_status")),
                        row.get("posting_date")
                    ))
                
                insert_sql = f"""
                    INSERT INTO jobs (title, company, location, salary_min, salary_max, salary_avg, experience, skills, industry, employment_type, remote_status, posting_date)
                    VALUES ({','.join([param_char] * 12)})
                """
                if db_type == "postgres":
                    from psycopg2.extras import execute_batch
                    execute_batch(cursor, insert_sql, jobs_to_insert, page_size=1000)
                else:
                    cursor.executemany(insert_sql, jobs_to_insert)
                conn.commit()
                print(f"Successfully seeded {len(jobs_to_insert)} jobs!")
        else:
            print(f"Warning: Cleaned CSV not found at {CLEANED_JOBS_CSV}. Seed skipped.")
            
    # 4. Seed Students if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        print("Seeding students table from student_profiles.csv...")
        if os.path.exists(STUDENTS_CSV):
            with open(STUDENTS_CSV, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                students_to_insert = []
                for row in reader:
                    students_to_insert.append((
                        row.get("student_id"),
                        float(row.get("cgpa", 0)),
                        int(row.get("skills_count", 0)),
                        int(row.get("internships", 0)),
                        int(row.get("projects", 0)),
                        int(row.get("certifications", 0)),
                        int(row.get("placed", 0))
                    ))
                
                insert_sql = f"""
                    INSERT INTO students (student_id, cgpa, skills_count, internships, projects, certifications, placed)
                    VALUES ({','.join([param_char] * 7)})
                """
                if db_type == "postgres":
                    from psycopg2.extras import execute_batch
                    execute_batch(cursor, insert_sql, students_to_insert, page_size=1000)
                else:
                    cursor.executemany(insert_sql, students_to_insert)
                conn.commit()
                print(f"Successfully seeded {len(students_to_insert)} student records!")
        else:
            print(f"Warning: Students CSV not found at {STUDENTS_CSV}. Seed skipped.")
            
    conn.close()

if __name__ == "__main__":
    init_db()
