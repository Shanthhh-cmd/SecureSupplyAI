import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.db_models import User, Project, ScanSession, ProjectType, SourceType, ScanStatus, AuditLog
from app.models.schemas import ProjectCreate, ProjectResponse
from app.services.intake import IntakeService
from app.services.scan_runner import ScanPipelineRunner

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.updated_at.desc()).all()
    results = []
    for p in projects:
        latest_scan = db.query(ScanSession).filter(ScanSession.project_id == p.id).order_by(ScanSession.created_at.desc()).first()
        scans_count = db.query(ScanSession).filter(ScanSession.project_id == p.id).count()
        
        results.append({
            "id": p.id,
            "user_id": p.user_id,
            "name": p.name,
            "description": p.description,
            "project_type": p.project_type,
            "source_type": p.source_type,
            "git_url": p.git_url,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "latest_scan_risk_score": latest_scan.risk_score if latest_scan else 0.0,
            "latest_scan_risk_level": latest_scan.risk_level if latest_scan else "Low",
            "scans_count": scans_count
        })
    return results

@router.post("", response_model=ProjectResponse)
async def create_project(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    project_type: str = Form("python"),
    source_type: str = Form("file"),
    git_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = Project(
        user_id=current_user.id,
        name=name,
        description=description,
        project_type=project_type,
        source_type=source_type,
        git_url=git_url
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    project_dir = os.path.join(settings.UPLOAD_DIR, f"project_{project.id}")
    os.makedirs(project_dir, exist_ok=True)

    target_path = project_dir

    if source_type == SourceType.GIT.value and git_url:
        target_path = IntakeService.clone_git_repo(git_url, project_dir)
    elif file:
        content = await file.read()
        target_path = IntakeService.process_file_upload(content, file.filename, project_dir)

    # Immediately trigger initial scan session
    scan = ScanSession(
        project_id=project.id,
        status=ScanStatus.PENDING.value
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Execute Scan Pipeline synchronously for immediate feedback
    ScanPipelineRunner.run_scan_pipeline(db, scan.id, target_path, project.name)

    db.add(AuditLog(user_id=current_user.id, action="PROJECT_CREATE", entity_type="project", entity_id=str(project.id)))
    db.commit()

    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "project_type": project.project_type,
        "source_type": project.source_type,
        "git_url": project.git_url,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "latest_scan_risk_score": scan.risk_score,
        "latest_scan_risk_level": scan.risk_level,
        "scans_count": 1
    }

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    latest_scan = db.query(ScanSession).filter(ScanSession.project_id == project.id).order_by(ScanSession.created_at.desc()).first()
    scans_count = db.query(ScanSession).filter(ScanSession.project_id == project.id).count()

    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "project_type": project.project_type,
        "source_type": project.source_type,
        "git_url": project.git_url,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "latest_scan_risk_score": latest_scan.risk_score if latest_scan else 0.0,
        "latest_scan_risk_level": latest_scan.risk_level if latest_scan else "Low",
        "scans_count": scans_count
    }

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()

    db.add(AuditLog(user_id=current_user.id, action="PROJECT_DELETE", entity_type="project", entity_id=str(project_id)))
    db.commit()

    return {"message": f"Project {project_id} deleted successfully"}
