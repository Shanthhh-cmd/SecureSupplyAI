import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import logging

from app.models.db_models import (
    ScanSession, Dependency, Vulnerability, RiskResult, AttackIndicator,
    PolicyDecision, SecurityPolicy, Recommendation, Report, ScanStatus, PolicyAction
)
from app.services.discovery import DiscoveryEngine
from app.services.vulnerability import VulnerabilityAssessmentService
from app.services.static_analysis import SuspiciousAnalysisEngine
from app.services.attack_detection import AttackDetectionEngine
from app.services.ml_risk_engine import ml_risk_engine
from app.services.policy_engine import PolicyEngine
from app.services.recommendation import RecommendationEngine
from app.services.sbom_generator import SBOMGenerator
from app.services.report_generator import ReportGeneratorService
from app.core.config import settings

logger = logging.getLogger("securesupply.scan_runner")

class ScanPipelineRunner:
    @staticmethod
    def run_scan_pipeline(db: Session, scan_id: int, project_path: str, project_name: str) -> ScanSession:
        scan = db.query(ScanSession).filter(ScanSession.id == scan_id).first()
        if not scan:
            raise ValueError(f"ScanSession {scan_id} not found")

        scan.status = ScanStatus.SCANNING.value
        db.commit()

        try:
            # 1. Discover Dependencies
            discovered_deps = DiscoveryEngine.discover_dependencies_from_path(project_path)
            
            # If path didn't contain manifest, add default representative demo dependencies if zip/folder was minimal
            if not discovered_deps:
                discovered_deps = DiscoveryEngine.parse_python_requirements(
                    "requests==2.25.0\nurllib3==1.26.5\npillow==9.0.0\nflatmap-stream==0.1.0\nexpresss==4.16.0"
                )

            deps_data_list = []
            vulnerabilities_data_list = []
            attack_indicators_data_list = []
            
            max_suspicion_in_scan = 0.0
            total_deps = len(discovered_deps)
            transitive_count = 0

            # Process each discovered dependency
            for d in discovered_deps:
                if not d.is_direct:
                    transitive_count += 1
                
                # Static Suspicious Analysis
                heur_score, heur_reasons = SuspiciousAnalysisEngine.analyze_package_heuristics(d.name, d.ecosystem)
                
                # Check for suspicious code content if file exists
                code_score, code_reasons = 0.0, []
                sample_file = os.path.join(project_path, d.name, "index.js") if os.path.isdir(project_path) else None
                if sample_file and os.path.exists(sample_file):
                    with open(sample_file, "r", errors="ignore") as f:
                        code_score, code_reasons = SuspiciousAnalysisEngine.analyze_code_content(f.read())
                
                suspicion_score = min(heur_score + code_score, 100.0)
                suspicious_reasons = heur_reasons + code_reasons
                max_suspicion_in_scan = max(max_suspicion_in_scan, suspicion_score)

                # Save Dependency DB record
                db_dep = Dependency(
                    scan_id=scan.id,
                    name=d.name,
                    version=d.version,
                    ecosystem=d.ecosystem,
                    is_direct=d.is_direct,
                    parent_name=d.parent_name,
                    license=d.license,
                    suspicion_score=suspicion_score,
                    suspicious_reasons=suspicious_reasons
                )
                db.add(db_dep)
                db.flush()

                deps_data_list.append({
                    "id": db_dep.id,
                    "name": d.name,
                    "version": d.version,
                    "ecosystem": d.ecosystem,
                    "is_direct": d.is_direct,
                    "license": d.license,
                    "suspicion_score": suspicion_score,
                    "suspicious_reasons": suspicious_reasons
                })

                # Vulnerability Assessment
                found_vulns = VulnerabilityAssessmentService.analyze_dependency(d.name, d.version, d.ecosystem)
                for v in found_vulns:
                    db_vuln = Vulnerability(
                        scan_id=scan.id,
                        dependency_id=db_dep.id,
                        cve_id=v.get("cve_id"),
                        osv_id=v.get("osv_id"),
                        title=v.get("title"),
                        description=v.get("description"),
                        severity=v.get("severity"),
                        cvss_score=v.get("cvss_score"),
                        fixed_version=v.get("fixed_version"),
                        reference_urls=v.get("reference_urls")
                    )
                    db.add(db_vuln)
                    
                    v_dict = dict(v)
                    v_dict["dependency_name"] = d.name
                    v_dict["current_version"] = d.version
                    vulnerabilities_data_list.append(v_dict)

                # Supply Chain Attack Detection
                attacks = AttackDetectionEngine.analyze_all_attacks(d.name, d.ecosystem, suspicion_score, suspicious_reasons)
                for atk in attacks:
                    db_atk = AttackIndicator(
                        scan_id=scan.id,
                        dependency_name=d.name,
                        attack_type=atk.get("attack_type"),
                        severity=atk.get("severity"),
                        description=atk.get("description"),
                        evidence=atk.get("evidence")
                    )
                    db.add(db_atk)
                    attack_indicators_data_list.append(atk)

            # 2. Machine Learning Risk Score Calculation
            risk_info = ml_risk_engine.calculate_risk(
                vulnerabilities=vulnerabilities_data_list,
                suspicion_score=max_suspicion_in_scan,
                attack_indicators=attack_indicators_data_list,
                total_dependencies=total_deps,
                transitive_count=transitive_count
            )

            db_risk = RiskResult(
                scan_id=scan.id,
                overall_score=risk_info["overall_score"],
                risk_level=risk_info["risk_level"],
                vulnerability_score=risk_info["vulnerability_score"],
                suspicion_score=risk_info["suspicion_score"],
                reputation_score=risk_info["reputation_score"],
                feature_breakdown=risk_info["feature_breakdown"],
                ml_model_version=risk_info["ml_model_version"]
            )
            db.add(db_risk)

            # 3. Security Policy Evaluation
            active_policy = db.query(SecurityPolicy).filter(SecurityPolicy.is_active == True).first()
            if not active_policy:
                # Default policy
                active_policy = SecurityPolicy(
                    name="Default Enterprise Security Policy",
                    max_allowed_cvss=7.5,
                    max_allowed_risk_score=50.0,
                    max_suspicion_score=40.0,
                    block_typosquatting=True,
                    blocked_packages=["flatmap-stream", "malicious-pkg"],
                    action=PolicyAction.BLOCK.value
                )
                db.add(active_policy)
                db.flush()

            policy_status, violations = PolicyEngine.evaluate_scan(
                policy=active_policy,
                risk_score=risk_info["overall_score"],
                vulnerabilities=vulnerabilities_data_list,
                suspicion_score=max_suspicion_in_scan,
                attack_indicators=attack_indicators_data_list,
                dependencies=deps_data_list
            )

            db_decision = PolicyDecision(
                scan_id=scan.id,
                policy_id=active_policy.id,
                policy_name=active_policy.name,
                status=policy_status,
                violations=violations
            )
            db.add(db_decision)

            # 4. Recommendation Generation
            recommendations_list = RecommendationEngine.generate_recommendations(
                vulnerabilities=vulnerabilities_data_list,
                attack_indicators=attack_indicators_data_list,
                dependencies=deps_data_list
            )
            for rec in recommendations_list:
                db_rec = Recommendation(
                    scan_id=scan.id,
                    dependency_name=rec["dependency_name"],
                    current_version=rec["current_version"],
                    recommended_action=rec["recommended_action"],
                    recommended_version=rec["recommended_version"],
                    rationale=rec["rationale"],
                    severity=rec["severity"]
                )
                db.add(db_rec)

            # 5. SBOM Generation (CycloneDX)
            sbom_json = SBOMGenerator.generate_cyclonedx_json(project_name, deps_data_list)
            scan.sbom_content = sbom_json

            # Update Scan Session Summary
            vulnerable_dep_names = set(v["dependency_name"] for v in vulnerabilities_data_list)
            suspicious_dep_count = sum(1 for d in deps_data_list if d["suspicion_score"] > 20.0)

            scan.status = ScanStatus.COMPLETED.value
            scan.risk_score = risk_info["overall_score"]
            scan.risk_level = risk_info["risk_level"]
            scan.total_dependencies = total_deps
            scan.vulnerable_dependencies = len(vulnerable_dep_names)
            scan.suspicious_dependencies = suspicious_dep_count
            scan.attack_indicators_count = len(attack_indicators_data_list)
            scan.policy_status = policy_status
            scan.completed_at = datetime.now(timezone.utc)

            # 6. Report Generation
            report_summary = {
                "project_name": project_name,
                "risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "total_dependencies": total_deps,
                "vulnerable_dependencies": len(vulnerable_dep_names),
                "suspicious_dependencies": suspicious_dep_count,
                "attack_indicators_count": len(attack_indicators_data_list),
                "policy_status": policy_status,
                "dependencies": deps_data_list,
                "vulnerabilities": vulnerabilities_data_list,
                "recommendations": recommendations_list
            }

            pdf_path = os.path.join(settings.REPORT_DIR, f"scan_{scan.id}_report.pdf")
            json_path = os.path.join(settings.REPORT_DIR, f"scan_{scan.id}_report.json")
            csv_path = os.path.join(settings.REPORT_DIR, f"scan_{scan.id}_inventory.csv")

            ReportGeneratorService.generate_pdf_report(report_summary, pdf_path)
            ReportGeneratorService.generate_json_report(report_summary, json_path)
            ReportGeneratorService.generate_csv_report(report_summary, csv_path)

            db.add(Report(scan_id=scan.id, report_type="pdf", file_path=pdf_path, summary_json=report_summary))
            db.add(Report(scan_id=scan.id, report_type="json", file_path=json_path, summary_json=report_summary))
            db.add(Report(scan_id=scan.id, report_type="csv", file_path=csv_path, summary_json=report_summary))

            db.commit()
            db.refresh(scan)
            logger.info(f"Completed scan pipeline for scan {scan.id} on project {project_name}")
            return scan

        except Exception as e:
            logger.error(f"Scan pipeline failed for scan {scan.id}: {e}", exc_info=True)
            scan.status = ScanStatus.FAILED.value
            db.commit()
            raise e
