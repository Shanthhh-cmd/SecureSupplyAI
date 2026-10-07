import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import User, Report, ScanSession

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    media_types = {
        "pdf": "application/pdf",
        "json": "application/json",
        "csv": "text/csv"
    }
    filename = os.path.basename(report.file_path)

    return FileResponse(
        path=report.file_path,
        media_type=media_types.get(report.report_type, "application/octet-stream"),
        filename=filename
    )

@router.get("/scan/{scan_id}")
def list_scan_reports(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = db.query(Report).filter(Report.scan_id == scan_id).all()
    return [
        {
            "id": r.id,
            "scan_id": r.scan_id,
            "report_type": r.report_type,
            "filename": os.path.basename(r.file_path),
            "created_at": r.created_at
        }
        for r in reports
    ]
