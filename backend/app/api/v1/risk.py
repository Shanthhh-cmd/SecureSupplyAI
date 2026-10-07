from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import User, RiskResult, ScanSession, Project
from app.services.ml_risk_engine import ml_risk_engine

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])

@router.get("/metrics")
def get_risk_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_projects = db.query(Project.id).filter(Project.user_id == current_user.id).subquery()
    scans = db.query(ScanSession).filter(ScanSession.project_id.in_(user_projects)).all()

    avg_risk = sum(s.risk_score for s in scans) / max(len(scans), 1)
    
    return {
        "average_risk_score": round(avg_risk, 1),
        "ml_model_status": "Active (RandomForestClassifier)",
        "ml_model_version": "1.0.0-random-forest",
        "scans_evaluated": len(scans)
    }
