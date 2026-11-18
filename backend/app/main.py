import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1 import (
    documents,
    courses,
    questions,
    templates,
    papers,
    validation,
    analytics,
    export
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Question Paper Design System assisting educational institutions in generating standardized, Bloom's Taxonomy-compliant examination papers.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enable CORS for local Vite dev server and production clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(courses.router, prefix=settings.API_V1_STR)
app.include_router(questions.router, prefix=settings.API_V1_STR)
app.include_router(templates.router, prefix=settings.API_V1_STR)
app.include_router(papers.router, prefix=settings.API_V1_STR)
app.include_router(validation.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(export.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    # Automatically create tables in database (SQLite/PostgreSQL)
    Base.metadata.create_all(bind=engine)
    # Automatically initialize seed fixtures if database is fresh
    try:
        from app.seed_data import seed_initial_data
        db = SessionLocal()
        seed_initial_data(db)
        db.close()
    except Exception as e:
        print(f"[Startup Seed Notice]: {e}")

# Mount built React frontend if dist exists
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not intercept API or docs routes
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = os.path.join(dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "system": "COGNITO: Cognitive Question Generation & Intelligent Taxonomy Optimizer",
            "version": "1.0.0",
            "status": "online",
            "docs_url": "/docs",
            "institution": "Vishwakarma Institute of Technology (VIT)"
        }
