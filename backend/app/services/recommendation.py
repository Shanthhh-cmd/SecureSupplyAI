from typing import List, Dict, Any

class RecommendationEngine:
    @staticmethod
    def generate_recommendations(
        vulnerabilities: List[Dict[str, Any]],
        attack_indicators: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        recs = []
        processed_deps = set()

        # 1. Recommendations for Vulnerabilities
        for v in vulnerabilities:
            dep_name = v.get("dependency_name") or v.get("package") or "Unknown"
            if dep_name in processed_deps or dep_name == "Unknown":
                continue
            
            fixed_ver = v.get("fixed_version", "latest release")
            severity = v.get("severity", "HIGH")
            cve = v.get("cve_id", "vulnerability")
            
            recs.append({
                "dependency_name": dep_name,
                "current_version": v.get("current_version", "1.0.0"),
                "recommended_action": "UPGRADE",
                "recommended_version": fixed_ver,
                "rationale": f"Upgrade {dep_name} to version {fixed_ver} to mitigate {severity} severity vulnerability ({cve}: {v.get('title')}).",
                "severity": severity
            })
            processed_deps.add(dep_name)

        # 2. Recommendations for Attack Indicators
        for a in attack_indicators:
            dep_name = a.get("dependency_name") or a.get("evidence", {}).get("package_name") or "Unknown"
            if dep_name in processed_deps or dep_name == "Unknown":
                continue
            
            attack_type = a.get("attack_type")
            if attack_type == "Typosquatting":
                target = a.get("evidence", {}).get("target_package", "the authentic library")
                recs.append({
                    "dependency_name": dep_name,
                    "current_version": "0.0.0",
                    "recommended_action": "REPLACE",
                    "recommended_version": target,
                    "rationale": f"Remove potential typosquatting package '{dep_name}' and replace with authentic upstream package '{target}'.",
                    "severity": "CRITICAL"
                })
            else:
                recs.append({
                    "dependency_name": dep_name,
                    "current_version": "0.0.0",
                    "recommended_action": "REMOVE",
                    "recommended_version": None,
                    "rationale": f"Immediately remove '{dep_name}' due to detected supply chain attack indicator: {a.get('description')}.",
                    "severity": "CRITICAL"
                })
            processed_deps.add(dep_name)

        # 3. Recommendations for Suspicious Packages
        for d in dependencies:
            dep_name = d.get("name")
            susp_score = d.get("suspicion_score", 0.0)
            if dep_name and dep_name not in processed_deps and susp_score >= 50.0:
                recs.append({
                    "dependency_name": dep_name,
                    "current_version": d.get("version", "1.0.0"),
                    "recommended_action": "REMOVE",
                    "recommended_version": None,
                    "rationale": f"Quarantine or remove '{dep_name}'. High suspicion score ({susp_score}/100) due to triggers: {', '.join(d.get('suspicious_reasons', []))}.",
                    "severity": "HIGH"
                })
                processed_deps.add(dep_name)

        return recs
