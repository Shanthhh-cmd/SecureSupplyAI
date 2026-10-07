from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SECURITY_ENGINEER = "security_engineer"
    DEVELOPER = "developer"

class ProjectType(str, enum.Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    MULTI = "multi"

class SourceType(str, enum.Enum):
    ZIP = "zip"
    FILE = "file"
    GIT = "git"
    SBOM = "sbom"

class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"

class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class VulnerabilitySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PolicyAction(str, enum.Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    RECOMMEND_UPDATE = "RECOMMEND_UPDATE"
    QUARANTINE = "QUARANTINE"
    BLOCK = "BLOCK"

class AttackType(str, enum.Enum):
    TYPOSQUATTING = "Typosquatting"
    DEPENDENCY_CONFUSION = "Dependency Confusion"
    PACKAGE_TAKEOVER = "Package Takeover"
    MALICIOUS_UPDATE = "Malicious Update"

class RecommendationAction(str, enum.Enum):
    UPGRADE = "UPGRADE"
    DOWNGRADE = "DOWNGRADE"
    REPLACE = "REPLACE"
    REMOVE = "REMOVE"
    PATCH = "PATCH"

# 1. User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.DEVELOPER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")

# 2. Project
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String, default=ProjectType.PYTHON.value)
    source_type = Column(String, default=SourceType.FILE.value)
    git_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects")
    scans = relationship("ScanSession", back_populates="project", cascade="all, delete-orphan")

# 3. ScanSession
class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default=ScanStatus.PENDING.value)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default=RiskLevel.LOW.value)
    total_dependencies = Column(Integer, default=0)
    vulnerable_dependencies = Column(Integer, default=0)
    suspicious_dependencies = Column(Integer, default=0)
    attack_indicators_count = Column(Integer, default=0)
    policy_status = Column(String, default=PolicyAction.ALLOW.value)
    sbom_content = Column(Text, nullable=True) # CycloneDX JSON content
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="scans")
    dependencies = relationship("Dependency", back_populates="scan", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    risk_result = relationship("RiskResult", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    attack_indicators = relationship("AttackIndicator", back_populates="scan", cascade="all, delete-orphan")
    policy_decisions = relationship("PolicyDecision", back_populates="scan", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="scan", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan", cascade="all, delete-orphan")

# 4. Dependency
class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    version = Column(String, nullable=False)
    ecosystem = Column(String, nullable=False) # PyPI, npm, Maven
    is_direct = Column(Boolean, default=True)
    parent_name = Column(String, nullable=True)
    license = Column(String, nullable=True)
    suspicion_score = Column(Float, default=0.0)
    suspicious_reasons = Column(JSON, default=list) # List of triggers e.g. ["install_script", "obfuscated_code"]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="dependencies")
    vulnerabilities = relationship("Vulnerability", back_populates="dependency", cascade="all, delete-orphan")

# 5. Vulnerability
class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)
    dependency_id = Column(Integer, ForeignKey("dependencies.id"), nullable=False)
    cve_id = Column(String, index=True, nullable=True)
    osv_id = Column(String, index=True, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, default=VulnerabilitySeverity.MEDIUM.value)
    cvss_score = Column(Float, default=0.0)
    fixed_version = Column(String, nullable=True)
    reference_urls = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="vulnerabilities")
    dependency = relationship("Dependency", back_populates="vulnerabilities")

# 6. RiskResult
class RiskResult(Base):
    __tablename__ = "risk_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False, unique=True)
    overall_score = Column(Float, default=0.0)
    risk_level = Column(String, default=RiskLevel.LOW.value)
    vulnerability_score = Column(Float, default=0.0)
    suspicion_score = Column(Float, default=0.0)
    reputation_score = Column(Float, default=0.0)
    feature_breakdown = Column(JSON, default=dict)
    ml_model_version = Column(String, default="1.0.0-rf")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="risk_result")

# 7. AttackIndicator
class AttackIndicator(Base):
    __tablename__ = "attack_indicators"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)
    dependency_name = Column(String, nullable=False)
    attack_type = Column(String, nullable=False) # Typosquatting, Dependency Confusion, etc.
    severity = Column(String, default=VulnerabilitySeverity.HIGH.value)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="attack_indicators")

# 8. SecurityPolicy
class SecurityPolicy(Base):
    __tablename__ = "security_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    max_allowed_cvss = Column(Float, default=7.0)
    max_allowed_risk_score = Column(Float, default=50.0)
    max_suspicion_score = Column(Float, default=40.0)
    block_typosquatting = Column(Boolean, default=True)
    blocked_packages = Column(JSON, default=list) # List of blocked package names
    action = Column(String, default=PolicyAction.BLOCK.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# 9. PolicyDecision
class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("security_policies.id"), nullable=True)
    policy_name = Column(String, nullable=False)
    status = Column(String, default=PolicyAction.ALLOW.value) # ALLOW, WARN, BLOCK, QUARANTINE
    violations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="policy_decisions")

# 10. Recommendation
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)
    dependency_name = Column(String, nullable=False)
    current_version = Column(String, nullable=False)
    recommended_action = Column(String, default=RecommendationAction.UPGRADE.value)
    recommended_version = Column(String, nullable=True)
    rationale = Column(Text, nullable=False)
    severity = Column(String, default=VulnerabilitySeverity.HIGH.value)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="recommendations")

# 11. Report
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)
    report_type = Column(String, nullable=False) # pdf, json, csv
    file_path = Column(String, nullable=False)
    summary_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("ScanSession", back_populates="reports")

# 12. AuditLog
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audit_logs")
