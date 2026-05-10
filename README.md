# IRAD Budget & Asset Tracker

A full-stack internal resource allocation and budget management system. Tracks project budgets, equipment assignments, and over-budget conditions via a REST API with an interactive web dashboard.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Automation:** CLI reporting script

## Features

- Full CRUD for projects, budget line items, and equipment assets
- Real-time over-budget detection and flagging
- Division-wide summary analytics (utilization %, remaining funds, portfolio value)
- CSV export for budget and asset reports
- Weekly CLI report generator
- Auto-generated interactive API docs (Swagger UI at `/docs`)

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Paradoxical7/irad-tracker.git
cd irad-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
cd backend
uvicorn main:app --reload
```

Dashboard → http://localhost:8000  
API Docs → http://localhost:8000/docs

### 4. Generate a weekly report
```bash
python scripts/weekly_report.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects/` | List all projects |
| POST | `/projects/` | Create a project |
| PATCH | `/projects/{id}` | Update a project |
| DELETE | `/projects/{id}` | Delete a project |
| GET | `/projects/{id}/budget` | List budget items |
| POST | `/projects/{id}/budget` | Add a budget item |
| GET | `/assets/` | List all assets |
| POST | `/assets/` | Register an asset |
| GET | `/reports/summary` | Division analytics |
| GET | `/reports/export/budget` | Download budget CSV |
| GET | `/reports/export/assets` | Download assets CSV |