"""
weekly_report.py
Run this script to generate a weekly summary report from the IRAD database.

Usage:
    python scripts/weekly_report.py
    python scripts/weekly_report.py --output ./reports/week_1.csv
"""

import argparse
import csv
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

def generate_report(output_path: str):
    db: Session = SessionLocal()
    try:
        projects = db.query(models.Project).all()
        assets = db.query(models.Asset).all()

        total_budget = sum(p.total_budget for p in projects)
        total_spent = sum(sum(i.spent for i in p.budget_items) for p in projects)
        over_budget = [
            p for p in projects
            if sum(i.spent for i in p.budget_items) > p.total_budget
        ]

        print("\n" + "=" * 55)
        print(f"  IRAD WEEKLY REPORT — {datetime.now().strftime('%B %d, %Y')}")
        print("=" * 55)
        print(f"  Projects       : {len(projects)}")
        print(f"  Total Budget   : ${total_budget:,.0f}")
        print(f"  Total Spent    : ${total_spent:,.0f}")
        print(f"  Remaining      : ${total_budget - total_spent:,.0f}")
        print(f"  Utilization    : {(total_spent/total_budget*100) if total_budget else 0:.1f}%")
        print(f"  Over Budget    : {len(over_budget)} project(s)")
        print(f"  Total Assets   : {len(assets)}")
        print("=" * 55)

        if over_budget:
            print("\n  ⚠  OVER-BUDGET PROJECTS:")
            for p in over_budget:
                spent = sum(i.spent for i in p.budget_items)
                print(f"     • {p.name} — ${spent:,.0f} spent / ${p.total_budget:,.0f} budget")

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Report Date", datetime.now().strftime("%Y-%m-%d")])
            writer.writerow([])
            writer.writerow(["== PROJECTS =="])
            writer.writerow(["Project", "Department", "Status", "Budget", "Spent", "Remaining", "Over Budget"])
            for p in projects:
                spent = sum(i.spent for i in p.budget_items)
                writer.writerow([
                    p.name, p.department, p.status.value,
                    p.total_budget, spent, p.total_budget - spent,
                    "YES" if spent > p.total_budget else "NO"
                ])
            writer.writerow([])
            writer.writerow(["== ASSETS =="])
            writer.writerow(["Asset", "Type", "Status", "Value", "Assigned To", "Project"])
            for a in assets:
                proj = db.query(models.Project).filter(models.Project.id == a.project_id).first()
                writer.writerow([
                    a.name, a.asset_type, a.status.value, a.value,
                    a.assigned_to or "—", proj.name if proj else "—"
                ])

        print(f"\n  ✓ Report saved to: {output_path}\n")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate IRAD weekly report.")
    parser.add_argument(
        "--output",
        default=f"reports/irad_report_{datetime.now().strftime('%Y%m%d')}.csv",
        help="Output CSV file path"
    )
    args = parser.parse_args()
    generate_report(args.output)