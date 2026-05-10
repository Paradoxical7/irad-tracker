import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary", response_model=schemas.DivisionSummary)
def division_summary(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    assets = db.query(models.Asset).all()

    total_budget = sum(p.total_budget for p in projects)
    total_spent = sum(
        sum(item.spent for item in p.budget_items) for p in projects
    )
    over_budget_projects = sum(
        1 for p in projects
        if sum(item.spent for item in p.budget_items) > p.total_budget
    )
    asset_total_value = sum(a.value for a in assets)
    utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0.0

    return schemas.DivisionSummary(
        total_projects=len(projects),
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_budget - total_spent,
        over_budget_projects=over_budget_projects,
        total_assets=len(assets),
        asset_total_value=asset_total_value,
        budget_utilization_pct=round(utilization, 2),
    )

@router.get("/export/budget", response_class=StreamingResponse)
def export_budget_csv(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Project", "Department", "Status", "Total Budget",
        "Category", "Allocated", "Spent", "Remaining", "Over Budget"
    ])

    for project in projects:
        for item in project.budget_items:
            remaining = item.allocated - item.spent
            writer.writerow([
                project.name, project.department, project.status.value,
                project.total_budget, item.category, item.allocated,
                item.spent, remaining,
                "YES" if item.spent > item.allocated else "NO",
            ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=irad_budget_report.csv"},
    )

@router.get("/export/assets", response_class=StreamingResponse)
def export_assets_csv(db: Session = Depends(get_db)):
    assets = db.query(models.Asset).all()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Asset Name", "Type", "Status", "Value", "Assigned To", "Project ID"])

    for asset in assets:
        writer.writerow([
            asset.name, asset.asset_type, asset.status.value,
            asset.value, asset.assigned_to or "—", asset.project_id or "—",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=irad_assets_report.csv"},
    )