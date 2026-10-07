import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.db_models import User, Project, ScanSession, ScanStatus, AuditLog
from app.models.schemas import ScanSessionResponse, ScanDetailResponse
from app.services.scan_runner import ScanPipelineRunner

router = APIRouter(prefix="/scans", tags=["Scans"])

@router.post("/trigger/{project_id}", response_model=ScanDetailResponse)
def trigger_scan(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = os.path.join(settings.UPLOAD_DIR, f"project_{project.id}")
    if not os.path.exists(project_dir):
        os.makedirs(project_dir, exist_ok=True)

    scan = ScanSession(
        project_id=project.id,
        status=ScanStatus.PENDING.value
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Run Scan Pipeline
    ScanPipelineRunner.run_scan_pipeline(db, scan.id, project_dir, project.name)

    db.add(AuditLog(user_id=current_user.id, action="SCAN_TRIGGER", entity_type="scan", entity_id=str(scan.id)))
    db.commit()

    return get_scan_detail(scan.id, db, current_user)

@router.get("/project/{project_id}", response_model=List[ScanSessionResponse])
def get_project_scans(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scans = db.query(ScanSession).filter(ScanSession.project_id == project_id).order_by(ScanSession.created_at.desc()).all()
    return scans

@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_detail(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(ScanSession).filter(ScanSession.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan session not found")

    # Format return detail
    deps_res = []
    for d in scan.dependencies:
        deps_res.append({
            "id": d.id,
            "scan_id": d.scan_id,
            "name": d.name,
            "version": d.version,
            "ecosystem": d.ecosystem,
            "is_direct": d.is_direct,
            "parent_name": d.parent_name,
            "license": d.license,
            "suspicion_score": d.suspicion_score,
            "suspicious_reasons": d.suspicious_reasons or [],
            "vulnerability_count": len(d.vulnerabilities)
        })

    vulns_res = []
    for v in scan.vulnerabilities:
        vulns_res.append({
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

    atks_res = scan.attack_indicators
    decisions_res = scan.policy_decisions
    recs_res = scan.recommendations
    risk_res = scan.risk_result

    return {
        "id": scan.id,
        "project_id": scan.project_id,
        "status": scan.status,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "total_dependencies": scan.total_dependencies,
        "vulnerable_dependencies": scan.vulnerable_dependencies,
        "suspicious_dependencies": scan.suspicious_dependencies,
        "attack_indicators_count": scan.attack_indicators_count,
        "policy_status": scan.policy_status,
        "created_at": scan.created_at,
        "completed_at": scan.completed_at,
        "dependencies": deps_res,
        "vulnerabilities": vulns_res,
        "risk_result": risk_res,
        "attack_indicators": atks_res,
        "policy_decisions": decisions_res,
        "recommendations": recs_res
    }

@router.get("/{scan_id}/sbom")
def get_scan_sbom(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(ScanSession).filter(ScanSession.id == scan_id).first()
    if not scan or not scan.sbom_content:
        raise HTTPException(status_code=404, detail="SBOM not found for this scan session")
    return {"sbom": scan.sbom_content}
