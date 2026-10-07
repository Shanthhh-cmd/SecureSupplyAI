from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.db_models import User, SecurityPolicy, AuditLog
from app.models.schemas import SecurityPolicyCreate, SecurityPolicyResponse

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("", response_model=List[SecurityPolicyResponse])
def list_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    policies = db.query(SecurityPolicy).all()
    if not policies:
        # Create default policy
        def_policy = SecurityPolicy(
            name="Enterprise Production Security Policy",
            description="Strict policy blocking CRITICAL vulnerabilities, high risk scores, and typosquatting attacks.",
            max_allowed_cvss=7.0,
            max_allowed_risk_score=50.0,
            max_suspicion_score=40.0,
            block_typosquatting=True,
            blocked_packages=["flatmap-stream", "malicious-pkg", "event-stream-malicious"],
            action="BLOCK",
            is_active=True
        )
        db.add(def_policy)
        db.commit()
        db.refresh(def_policy)
        policies = [def_policy]
    return policies

@router.post("", response_model=SecurityPolicyResponse)
def create_policy(policy_in: SecurityPolicyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if policy_in.is_active:
        # Deactivate previous active policies
        db.query(SecurityPolicy).update({"is_active": False})

    policy = SecurityPolicy(
        name=policy_in.name,
        description=policy_in.description,
        max_allowed_cvss=policy_in.max_allowed_cvss,
        max_allowed_risk_score=policy_in.max_allowed_risk_score,
        max_suspicion_score=policy_in.max_suspicion_score,
        block_typosquatting=policy_in.block_typosquatting,
        blocked_packages=policy_in.blocked_packages,
        action=policy_in.action.value,
        is_active=policy_in.is_active
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    db.add(AuditLog(user_id=current_user.id, action="POLICY_CREATE", entity_type="security_policy", entity_id=str(policy.id)))
    db.commit()

    return policy

@router.put("/{policy_id}/activate", response_model=SecurityPolicyResponse)
def activate_policy(policy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    policy = db.query(SecurityPolicy).filter(SecurityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    db.query(SecurityPolicy).update({"is_active": False})
    policy.is_active = True
    db.commit()
    db.refresh(policy)

    db.add(AuditLog(user_id=current_user.id, action="POLICY_ACTIVATE", entity_type="security_policy", entity_id=str(policy.id)))
    db.commit()

    return policy
