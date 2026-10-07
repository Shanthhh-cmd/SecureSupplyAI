from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import User, Vulnerability, Dependency, ScanSession, Project
from app.models.schemas import VulnerabilityResponse

router = APIRouter(prefix="/vulnerabilities", tags=["Vulnerabilities"])

@router.get("", response_model=List[VulnerabilityResponse])
def list_vulnerabilities(
    severity: Optional[str] = Query(None),
    cve: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Vulnerability).join(ScanSession).join(Project).filter(Project.user_id == current_user.id)
    
    if severity:
        query = query.filter(Vulnerability.severity == severity.upper())
    if cve:
        query = query.filter(Vulnerability.cve_id.ilike(f"%{cve}%"))
        
    vulns = query.order_by(Vulnerability.cvss_score.desc()).all()
    
    results = []
    for v in vulns:
        results.append({
            "id": v.id,
            "scan_id": v.scan_id,
            "dependency_id": v.dependency_id,
            "dependency_name": v.dependency.name if v.dependency else "N/A",
            "dependency_version": v.dependency.version if v.dependency else "N/A",
            "cve_id": v.cve_id,
            "osv_id": v.osv_id,
            "title": v.title,
            "description": v.description,
            "severity": v.severity,
            "cvss_score": v.cvss_score,
            "fixed_version": v.fixed_version,
            "reference_urls": v.reference_urls or []
        })
    return results
