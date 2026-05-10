from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine
import models
from routers import projects, assets, reports

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IRAD Budget & Asset Tracker",
    description="A REST API for tracking project budgets, equipment assignments, and division-wide reporting.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(assets.router)
app.include_router(reports.router)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("../frontend/index.html")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "IRAD Tracker"}