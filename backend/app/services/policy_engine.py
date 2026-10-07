from typing import List, Dict, Any, Tuple
from app.models.db_models import SecurityPolicy, PolicyAction

class PolicyEngine:
    @staticmethod
    def evaluate_scan(
        policy: SecurityPolicy,
        risk_score: float,
        vulnerabilities: List[Dict[str, Any]],
        suspicion_score: float,
        attack_indicators: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        violations = []

        # 1. CVSS Threshold Check
        max_cvss = max([v.get("cvss_score", 0.0) for v in vulnerabilities], default=0.0)
        if max_cvss > policy.max_allowed_cvss:
            violations.append(
                f"CVSS Violation: Maximum CVSS found ({max_cvss}) exceeds policy limit ({policy.max_allowed_cvss})"
            )

        # 2. Risk Score Threshold Check
        if risk_score > policy.max_allowed_risk_score:
            violations.append(
                f"Risk Score Violation: Overall Risk Score ({risk_score}) exceeds policy limit ({policy.max_allowed_risk_score})"
            )

        # 3. Suspicion Score Threshold Check
        if suspicion_score > policy.max_suspicion_score:
            violations.append(
                f"Suspicion Violation: Max Suspicion Score ({suspicion_score}) exceeds policy limit ({policy.max_suspicion_score})"
            )

        # 4. Typosquatting Check
        if policy.block_typosquatting:
            typo_attacks = [a for a in attack_indicators if a.get("attack_type") == "Typosquatting"]
            if typo_attacks:
                violations.append(
                    f"Attack Indicator Violation: {len(typo_attacks)} typosquatting attack indicator(s) detected"
                )

        # 5. Blocked Package List Check
        blocked_set = set(p.lower() for p in policy.blocked_packages or [])
        for d in dependencies:
            if d.get("name", "").lower() in blocked_set:
                violations.append(
                    f"Blocked Package Violation: Dependency '{d.get('name')}' is on the organization blacklist"
                )

        # Determine decision status
        if not violations:
            status = PolicyAction.ALLOW.value
        else:
            status = policy.action if policy.action else PolicyAction.BLOCK.value

        return status, violations
