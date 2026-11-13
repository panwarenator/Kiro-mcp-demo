import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "talent.db")

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

# Table 1: Departments
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    dept_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_name   TEXT NOT NULL UNIQUE,
    cost_center TEXT NOT NULL,
    lead_name   TEXT NOT NULL
);
""")

# Table 2: Employees
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_code         TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    email            TEXT NOT NULL UNIQUE,
    dept_id          INTEGER NOT NULL,
    experience_years INTEGER NOT NULL,
    bench_status     TEXT NOT NULL CHECK(bench_status IN (
                         'Available', 'Partially Allocated', 'Fully Allocated')),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
);
""")

# Table 3: Skills
cursor.execute("""
CREATE TABLE IF NOT EXISTS skills (
    skill_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    category   TEXT NOT NULL
);
""")

# Table 4: Employee Skills (Junction)
cursor.execute("""
CREATE TABLE IF NOT EXISTS employee_skills (
    emp_id            INTEGER NOT NULL,
    skill_id          INTEGER NOT NULL,
    proficiency_level TEXT NOT NULL CHECK(proficiency_level IN (
                          'Beginner', 'Intermediate', 'Expert')),
    is_primary        INTEGER NOT NULL DEFAULT 0 CHECK(is_primary IN (0, 1)),
    PRIMARY KEY (emp_id, skill_id),
    FOREIGN KEY (emp_id)   REFERENCES employees(emp_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id)  ON DELETE CASCADE
);
""")

# Table 5: Projects
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    project_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code TEXT NOT NULL UNIQUE,
    client_name  TEXT NOT NULL,
    project_name TEXT NOT NULL,
    start_date   TEXT NOT NULL,
    end_date     TEXT
);
""")

# Table 6: Project Allocations (Junction)
cursor.execute("""
CREATE TABLE IF NOT EXISTS project_allocations (
    allocation_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id                INTEGER NOT NULL,
    project_id            INTEGER NOT NULL,
    role                  TEXT NOT NULL,
    allocation_percentage INTEGER NOT NULL CHECK(allocation_percentage BETWEEN 1 AND 100),
    is_billable           INTEGER NOT NULL CHECK(is_billable IN (0, 1)),
    FOREIGN KEY (emp_id)     REFERENCES employees(emp_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT
);
""")

# Seed Data
departments = [
    ("AI & Emerging Tech",   "CC-AI-901",   "Dr. Rajesh Kaul"),
    ("Core BFSI Banking",    "CC-BFSI-104", "Meenakshi Iyer"),
    ("Cloud & DevSecOps",    "CC-OPS-302",  "Suresh Menon"),
    ("Digital Solutions",    "CC-DIGI-505", "Anita Roy")
]
cursor.executemany("INSERT INTO departments (dept_name, cost_center, lead_name) VALUES (?, ?, ?);", departments)

skills = [
    ("Python & FastMCP",              "Agentic AI"),
    ("LangChain & LLMOps",            "GenAI"),
    ("Spring Boot & Microservices",   "Backend"),
    ("React & Next.js",               "Frontend"),
    ("AWS Solution Architecture",     "Cloud Infrastructure"),
    ("Financial Transaction Systems", "BFSI Domain")
]
cursor.executemany("INSERT INTO skills (skill_name, category) VALUES (?, ?);", skills)

employees = [
    ("EMP101", "Aarav Sharma", "aarav.sharma@corp.com",  1, 6, "Available"),
    ("EMP102", "Pooja Patel",  "pooja.patel@corp.com",   4, 4, "Fully Allocated"),
    ("EMP103", "Rohan Verma",  "rohan.verma@corp.com",   1, 5, "Partially Allocated"),
    ("EMP104", "Sneha Nair",   "sneha.nair@corp.com",    3, 7, "Available"),
    ("EMP105", "Vikram Singh", "vikram.singh@corp.com",  2, 8, "Fully Allocated")
]
cursor.executemany("""
INSERT INTO employees (emp_code, name, email, dept_id, experience_years, bench_status)
VALUES (?, ?, ?, ?, ?, ?);
""", employees)

employee_skills = [
    (1, 1, "Expert",       1),
    (1, 2, "Expert",       0),
    (1, 5, "Intermediate", 0),
    (2, 4, "Expert",       1),
    (3, 2, "Expert",       1),
    (3, 1, "Intermediate", 0),
    (4, 5, "Expert",       1),
    (5, 3, "Expert",       1),
    (5, 6, "Expert",       0)
]
cursor.executemany("""
INSERT INTO employee_skills (emp_id, skill_id, proficiency_level, is_primary)
VALUES (?, ?, ?, ?);
""", employee_skills)

projects = [
    ("PRJ-BFSI-01", "Global Metro Bank", "Core Ledger Modernization",    "2026-01-15", "2026-12-31"),
    ("PRJ-RET-09",  "OmniRetail UK",     "Customer Intelligence Portal", "2026-03-01", "2026-08-30"),
    ("PRJ-FIN-12",  "Apex FinTech",      "Real-Time Fraud Detection",    "2026-02-10", "2026-11-15")
]
cursor.executemany("""
INSERT INTO projects (project_code, client_name, project_name, start_date, end_date)
VALUES (?, ?, ?, ?, ?);
""", projects)

allocations = [
    (2, 2, "Lead UI Engineer",         100, 1),
    (3, 3, "GenAI Architect",           50, 1),
    (5, 1, "Principal Java Architect", 100, 1)
]
cursor.executemany("""
INSERT INTO project_allocations (emp_id, project_id, role, allocation_percentage, is_billable)
VALUES (?, ?, ?, ?, ?);
""", allocations)

conn.commit()
conn.close()
print("talent.db created successfully with 6 tables and seed data.")
