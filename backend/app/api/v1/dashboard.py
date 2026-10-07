from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import User, Project, ScanSession, Dependency, Vulnerability, AttackIndicator
from app.models.schemas import ExecutiveDashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=ExecutiveDashboardSummary)
def get_executive_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_projects = select(Project.id).where(Project.user_id == current_user.id)
    
    total_projects = db.query(Project).filter(Project.user_id == current_user.id).count()
    scans = db.query(ScanSession).filter(ScanSession.project_id.in_(user_projects)).all()
    total_scans = len(scans)

    total_deps = db.query(Dependency).join(ScanSession).filter(ScanSession.project_id.in_(user_projects)).count()
    vulnerable_deps = db.query(func.count(func.distinct(Vulnerability.dependency_id))).join(ScanSession).filter(ScanSession.project_id.in_(user_projects)).scalar() or 0

    critical_count = db.query(Vulnerability).join(ScanSession).filter(
        ScanSession.project_id.in_(user_projects), Vulnerability.severity == "CRITICAL"
    ).count()
    
    high_count = db.query(Vulnerability).join(ScanSession).filter(
        ScanSession.project_id.in_(user_projects), Vulnerability.severity == "HIGH"
    ).count()

    medium_count = db.query(Vulnerability).join(ScanSession).filter(
        ScanSession.project_id.in_(user_projects), Vulnerability.severity == "MEDIUM"
    ).count()

    low_count = db.query(Vulnerability).join(ScanSession).filter(
        ScanSession.project_id.in_(user_projects), Vulnerability.severity == "LOW"
    ).count()

    blocked_deps = db.query(ScanSession).filter(
        ScanSession.project_id.in_(user_projects), ScanSession.policy_status == "BLOCK"
    ).count()

    # Risk Distribution
    risk_distribution = {
        "Low": sum(1 for s in scans if s.risk_level == "Low"),
        "Medium": sum(1 for s in scans if s.risk_level == "Medium"),
        "High": sum(1 for s in scans if s.risk_level == "High"),
        "Critical": sum(1 for s in scans if s.risk_level == "Critical")
    }

    # Severity Breakdown
    severity_breakdown = {
        "CRITICAL": critical_count,
        "HIGH": high_count,
        "MEDIUM": medium_count,
        "LOW": low_count
    }

    # Recent Scans
    recent_scans = db.query(ScanSession).filter(ScanSession.project_id.in_(user_projects)).order_by(ScanSession.created_at.desc()).limit(5).all()

    # Scan Trends
    scan_trends = []
    ordered_scans = db.query(ScanSession).filter(ScanSession.project_id.in_(user_projects)).order_by(ScanSession.created_at.asc()).limit(10).all()
    for s in ordered_scans:
        scan_trends.append({
            "date": s.created_at.strftime("%Y-%m-%d %H:%M"),
            "risk_score": s.risk_score,
            "vulnerabilities": s.vulnerable_dependencies,
            "total_deps": s.total_dependencies
        })

    return {
        "total_projects": total_projects,
        "total_scans": total_scans,
        "total_dependencies": total_deps,
        "vulnerable_dependencies": vulnerable_deps,
        "critical_findings": critical_count,
        "high_findings": high_count,
        "blocked_dependencies": blocked_deps,
        "risk_distribution": risk_distribution,
        "severity_breakdown": severity_breakdown,
        "recent_scans": recent_scans,
        "scan_trends": scan_trends
    }
