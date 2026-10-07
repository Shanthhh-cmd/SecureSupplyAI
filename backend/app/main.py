import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.logging import setup_logging
from app.models.db_models import User, UserRole, SecurityPolicy, Project, ScanSession, ScanStatus
from app.core.security import get_password_hash

# API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.scans import router as scans_router
from app.api.v1.vulnerabilities import router as vulns_router
from app.api.v1.risk import router as risk_router
from app.api.v1.policies import router as policies_router
from app.api.v1.reports import router as reports_router
from app.api.v1.dashboard import router as dashboard_router
from app.services.scan_runner import ScanPipelineRunner

setup_logging()
logger = logging.getLogger("securesupply.main")

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            logger.info("Seeding default demo user and initial security policy...")
            admin_user = User(
                email="admin@securesupply.ai",
                hashed_password=get_password_hash("admin123"),
                full_name="Security Admin",
                role=UserRole.ADMIN.value
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            default_policy = SecurityPolicy(
                name="Enterprise Production Policy",
                description="Blocks high severity vulnerabilities and typosquatting attacks.",
                max_allowed_cvss=7.0,
                max_allowed_risk_score=50.0,
                max_suspicion_score=40.0,
                block_typosquatting=True,
                blocked_packages=["flatmap-stream", "malicious-pkg"],
                action="BLOCK",
                is_active=True
            )
            db.add(default_policy)
            db.commit()

            # Seed Demo Project & Initial Scan
            demo_proj = Project(
                user_id=admin_user.id,
                name="SecureSupply AI Demo Gateway",
                description="Production API Gateway microservice dependency scan target",
                project_type="python",
                source_type="file"
            )
            db.add(demo_proj)
            db.commit()
            db.refresh(demo_proj)

            demo_scan = ScanSession(
                project_id=demo_proj.id,
                status=ScanStatus.PENDING.value
            )
            db.add(demo_scan)
            db.commit()

            # Run initial scan pipeline
            demo_dir = os.path.join(settings.UPLOAD_DIR, f"project_{demo_proj.id}")
            os.makedirs(demo_dir, exist_ok=True)
            with open(os.path.join(demo_dir, "requirements.txt"), "w") as f:
                f.write("requests==2.25.0\nurllib3==1.26.5\npillow==9.0.0\nflatmap-stream==0.1.0\nreqeusts==2.25.0\n")

            ScanPipelineRunner.run_scan_pipeline(db, demo_scan.id, demo_dir, demo_proj.name)
            logger.info("Demo data seed complete!")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_demo_data()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal platform error occurred. Please check system logs."}
    )

# Include Routers under API V1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(scans_router, prefix=settings.API_V1_STR)
app.include_router(vulns_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(policies_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
