# HireFlow — Smart Recruitment and Applicant Tracking System (ATS)

> A modern, full-stack recruitment platform and applicant tracking system built with **Django 5**, **Django REST Framework**, and **Bootstrap 5**. Designed as an enterprise-grade portfolio project demonstrating role-based workflows, database integrity, recruitment pipelines, RESTful APIs, and administrative analytics.

---

## Key Features

###  Module 1: Recruiter Dashboard
- **Job Vacancy Management**: Create, edit, pause, and close job postings with detailed requirements, salary ranges, location types (Remote/Hybrid/Onsite), and deadlines.
- **Candidate Pipeline**: Visual Kanban and tabular views tracking applicants through four clear stages:
  $$\text{Applied} \longrightarrow \text{Shortlisted} \longrightarrow \text{Interview Scheduled} \longrightarrow \text{Selected / Rejected}$$
- **Interview Scheduling**: Schedule video, phone, or in-person rounds with date/time pickers, meeting links, and interviewer notes.
- **Candidate Profiles**: View applicant portfolios, contact links, experience details, and download resumes.
- **CSV Data Export**: One-click candidate data export for external spreadsheet workflows.

###  Module 2: Applicant Portal
- **Authentication & User Profiles**: Sign up as an applicant, upload resumes, add skills tags, and customize social/portfolio links.
- **Job Discovery & Search**: Multi-filter search by keywords, job categories, employment types, experience levels, and salary.
- **One-Click Application**: Apply using an existing uploaded profile resume or upload a tailored resume per application.
- **Duplicate Prevention**: Database-level unique constraint (`unique_together = ('job', 'applicant')`) prevents accidental duplicate submissions.
- **Application Status Tracker**: Real-time status tracker and audit trail showing every milestone in the recruitment process.
- **Application Withdrawal**: Safe withdrawal option for candidates prior to final decision stages.

###  Module 3: Admin Analytics & User Management
- **Platform Analytics**: Interactive **Chart.js** visualizations showing application status distribution and top hiring categories.
- **User Management**: View, filter by role (Admin, Recruiter, Applicant), search, and toggle user active/deactive status.
- **Django Admin Integration**: Full administrative control with inline interview history and custom admin actions.

###  Module 4: RESTful API (Django REST Framework)
- Complete REST endpoints for Jobs, Job Categories, Applications, Interviews, and Dashboard Stats.
- Search filters, status filters, and pagination out-of-the-box.
- Role-based API permissions ensuring secure recruiter and applicant isolation.

---

##  Technology Stack

- **Backend**: Python 3.10+, Django 5.x, Django REST Framework (DRF)
- **Database**: SQLite (Development) / PostgreSQL-ready (Production)
- **Frontend**: Django Templates, Bootstrap 5, Bootstrap Icons, Chart.js
- **Forms & UI**: `django-crispy-forms` + `crispy-bootstrap5`
- **File Management**: Django media file storage for PDF resumes and avatars

---

##  Quickstart Guide

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-username/HireFlow.git
cd HireFlow

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```bash
python manage.py migrate
```

### 4. Seed Realistic Demo Data
Populate the database with pre-configured recruiters, candidates, jobs, applications, and scheduled interviews:
```bash
python manage.py seed_data
```

### 5. Run the Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

##  Demo Accounts

All demo accounts are automatically initialized by `python manage.py seed_data`:

| Role | Email | Password | What You Can Test |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@hireflow.dev` | `adminpassword123` | Platform analytics, User management, Django admin |
| **Recruiter** | `sarah@acme.com` | `recruiter123` | Post jobs, candidate Kanban pipeline, schedule interviews |
| **Recruiter** | `david@cloudscale.io` | `recruiter123` | Manage infrastructure jobs, candidate review & status update |
| **Applicant** | `john@hireflow.dev` | `applicant123` | View application pipeline status, interview details |
| **Applicant** | `jane@hireflow.dev` | `applicant123` | Search jobs, submit application, profile editing |
| **Applicant** | `alex@hireflow.dev` | `applicant123` | View selected status, past interview feedback |

---

##  Running Automated Tests

Run the full automated test suite covering models, views, duplicate prevention, and API endpoints:
```bash
python manage.py test
```

Test coverage includes:
- `jobs`: Job listing, searching, filtering, permissions, and view counter increments.
- `applications`: Application submission, duplicate application prevention, recruiter status progression, candidate withdrawal.
- `accounts`: User registration by role, login, logout, profile handling.
- `api`: DRF endpoints, authentication permissions, status updates via REST.

---

##  API Reference

Base URL: `/api/`

| Endpoint | Method | Description | Access |
| :--- | :--- | :--- | :--- |
| `/api/jobs/` | `GET`, `POST` | List active jobs or create new job posting | Public / Recruiter |
| `/api/jobs/{id}/` | `GET`, `PUT`, `DELETE` | Job details or update | Public / Owner Recruiter |
| `/api/categories/` | `GET` | List all job categories | Public |
| `/api/applications/` | `GET`, `POST` | List user applications or apply for a job | Authenticated |
| `/api/applications/{id}/update_status/` | `POST` | Move candidate to next pipeline stage | Recruiter / Admin |
| `/api/interviews/` | `GET`, `POST` | View or schedule interviews | Recruiter / Admin |
| `/api/stats/` | `GET` | Dashboard pipeline metrics & counts | Authenticated |
| `/api/admin/users/` | `GET` | User management | Admin Only |

---

##  Project Directory Structure

```text
HireFlow/
├── accounts/               # Custom user model (roles: Admin, Recruiter, Applicant) & profiles
├── jobs/                   # Job categories, job listings, search & filters, seed command
├── applications/           # Job applications, pipeline stages, interviews & status history
├── dashboard/              # Recruiter Kanban, Applicant portal & Admin analytics
├── api/                    # Django REST Framework viewsets and serializers
├── templates/              # Modern Bootstrap 5 templates with custom glassmorphism styling
│   ├── base.html           # Master navigation and layout
│   ├── accounts/           # Login, register, profile views
│   ├── jobs/               # Job list, job details, job creation forms
│   ├── applications/       # Apply form, tracking, detail, schedule interview
│   └── dashboard/          # Recruiter, Applicant, and Admin overview dashboards
├── static/                 # CSS styling, Chart.js visualizations, responsive JS
├── media/                  # User avatars and uploaded candidate resumes
└── hireflow/               # Core project settings and URL configuration
```

---

## 📜 License
This project is open-source under the MIT License.
