from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.models.db_models import (
    UserRole, ProjectType, SourceType, ScanStatus, RiskLevel,
    VulnerabilitySeverity, PolicyAction, AttackType, RecommendationAction
)

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.DEVELOPER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: ProjectType = ProjectType.PYTHON
    source_type: SourceType = SourceType.FILE
    git_url: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    latest_scan_risk_score: Optional[float] = None
    latest_scan_risk_level: Optional[str] = None
    scans_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

# Dependency Schemas
class DependencyResponse(BaseModel):
    id: int
    scan_id: int
    name: str
    version: str
    ecosystem: str
    is_direct: bool
    parent_name: Optional[str] = None
    license: Optional[str] = None
    suspicion_score: float
    suspicious_reasons: List[str] = []
    vulnerability_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

# Vulnerability Schemas
class VulnerabilityResponse(BaseModel):
    id: int
    scan_id: int
    dependency_id: int
    dependency_name: Optional[str] = None
    dependency_version: Optional[str] = None
    cve_id: Optional[str] = None
    osv_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: VulnerabilitySeverity
    cvss_score: float
    fixed_version: Optional[str] = None
    reference_urls: List[str] = []

    model_config = ConfigDict(from_attributes=True)

# Attack Indicator Schemas
class AttackIndicatorResponse(BaseModel):
    id: int
    scan_id: int
    dependency_name: str
    attack_type: str
    severity: VulnerabilitySeverity
    description: str
    evidence: Dict[str, Any] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Policy Schemas
class SecurityPolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_allowed_cvss: float = 7.0
    max_allowed_risk_score: float = 50.0
    max_suspicion_score: float = 40.0
    block_typosquatting: bool = True
    blocked_packages: List[str] = []
    action: PolicyAction = PolicyAction.BLOCK
    is_active: bool = True

class SecurityPolicyCreate(SecurityPolicyBase):
    pass

class SecurityPolicyResponse(SecurityPolicyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PolicyDecisionResponse(BaseModel):
    id: int
    scan_id: int
    policy_name: str
    status: PolicyAction
    violations: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    scan_id: int
    dependency_name: str
    current_version: str
    recommended_action: RecommendationAction
    recommended_version: Optional[str] = None
    rationale: str
    severity: VulnerabilitySeverity
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Risk Result Schema
class RiskResultResponse(BaseModel):
    id: int
    scan_id: int
    overall_score: float
    risk_level: RiskLevel
    vulnerability_score: float
    suspicion_score: float
    reputation_score: float
    feature_breakdown: Dict[str, Any] = {}
    ml_model_version: str

    model_config = ConfigDict(from_attributes=True)

# Scan Session Schemas
class ScanSessionResponse(BaseModel):
    id: int
    project_id: int
    status: ScanStatus
    risk_score: float
    risk_level: RiskLevel
    total_dependencies: int
    vulnerable_dependencies: int
    suspicious_dependencies: int
    attack_indicators_count: int
    policy_status: PolicyAction
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ScanDetailResponse(ScanSessionResponse):
    dependencies: List[DependencyResponse] = []
    vulnerabilities: List[VulnerabilityResponse] = []
    risk_result: Optional[RiskResultResponse] = None
    attack_indicators: List[AttackIndicatorResponse] = []
    policy_decisions: List[PolicyDecisionResponse] = []
    recommendations: List[RecommendationResponse] = []

# Executive Dashboard Summary Schema
class ExecutiveDashboardSummary(BaseModel):
    total_projects: int
    total_scans: int
    total_dependencies: int
    vulnerable_dependencies: int
    critical_findings: int
    high_findings: int
    blocked_dependencies: int
    risk_distribution: Dict[str, int]
    severity_breakdown: Dict[str, int]
    recent_scans: List[ScanSessionResponse]
    scan_trends: List[Dict[str, Any]]
