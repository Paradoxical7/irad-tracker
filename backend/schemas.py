from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import ProjectStatus, AssetStatus

# ── Project ──────────────────────────────────────────────
class ProjectCreate(BaseModel):
    name: str
    department: str
    total_budget: float = Field(gt=0)
    status: ProjectStatus = ProjectStatus.active

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    total_budget: Optional[float] = Field(default=None, gt=0)
    status: Optional[ProjectStatus] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    department: str
    total_budget: float
    status: ProjectStatus
    created_at: datetime
    total_spent: float = 0.0
    over_budget: bool = False

    class Config:
        from_attributes = True

# ── Budget Item ───────────────────────────────────────────
class BudgetItemCreate(BaseModel):
    category: str
    allocated: float = Field(gt=0)
    spent: float = Field(default=0.0, ge=0)

class BudgetItemUpdate(BaseModel):
    category: Optional[str] = None
    allocated: Optional[float] = Field(default=None, gt=0)
    spent: Optional[float] = Field(default=None, ge=0)

class BudgetItemOut(BaseModel):
    id: int
    project_id: int
    category: str
    allocated: float
    spent: float
    over_budget: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

# ── Asset ─────────────────────────────────────────────────
class AssetCreate(BaseModel):
    name: str
    asset_type: str
    value: float = Field(gt=0)
    assigned_to: Optional[str] = None
    project_id: Optional[int] = None
    status: AssetStatus = AssetStatus.available

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    value: Optional[float] = Field(default=None, gt=0)
    assigned_to: Optional[str] = None
    project_id: Optional[int] = None
    status: Optional[AssetStatus] = None

class AssetOut(BaseModel):
    id: int
    name: str
    asset_type: str
    assigned_to: Optional[str]
    project_id: Optional[int]
    status: AssetStatus
    value: float
    created_at: datetime

    class Config:
        from_attributes = True

# ── Summary ───────────────────────────────────────────────
class DivisionSummary(BaseModel):
    total_projects: int
    total_budget: float
    total_spent: float
    total_remaining: float
    over_budget_projects: int
    total_assets: int
    asset_total_value: float
    budget_utilization_pct: float