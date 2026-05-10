from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas

router = APIRouter(prefix="/projects", tags=["Projects"])

def _enrich_project(project: models.Project) -> schemas.ProjectOut:
    total_spent = sum(item.spent for item in project.budget_items)
    return schemas.ProjectOut(
        id=project.id,
        name=project.name,
        department=project.department,
        total_budget=project.total_budget,
        status=project.status,
        created_at=project.created_at,
        total_spent=total_spent,
        over_budget=total_spent > project.total_budget,
    )

@router.get("/", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return [_enrich_project(p) for p in db.query(models.Project).all()]

@router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if db.query(models.Project).filter(models.Project.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Project name already exists.")
    project = models.Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return _enrich_project(project)

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return _enrich_project(project)

@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _enrich_project(project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    db.delete(project)
    db.commit()

@router.get("/{project_id}/budget", response_model=List[schemas.BudgetItemOut])
def list_budget_items(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return [
        schemas.BudgetItemOut(**{**item.__dict__, "over_budget": item.spent > item.allocated})
        for item in project.budget_items
    ]

@router.post("/{project_id}/budget", response_model=schemas.BudgetItemOut, status_code=status.HTTP_201_CREATED)
def add_budget_item(project_id: int, payload: schemas.BudgetItemCreate, db: Session = Depends(get_db)):
    if not db.query(models.Project).filter(models.Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found.")
    item = models.BudgetItem(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return schemas.BudgetItemOut(**{**item.__dict__, "over_budget": item.spent > item.allocated})

@router.patch("/{project_id}/budget/{item_id}", response_model=schemas.BudgetItemOut)
def update_budget_item(project_id: int, item_id: int, payload: schemas.BudgetItemUpdate, db: Session = Depends(get_db)):
    item = db.query(models.BudgetItem).filter(
        models.BudgetItem.id == item_id,
        models.BudgetItem.project_id == project_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Budget item not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return schemas.BudgetItemOut(**{**item.__dict__, "over_budget": item.spent > item.allocated})

@router.delete("/{project_id}/budget/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget_item(project_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.BudgetItem).filter(
        models.BudgetItem.id == item_id,
        models.BudgetItem.project_id == project_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Budget item not found.")
    db.delete(item)
    db.commit()