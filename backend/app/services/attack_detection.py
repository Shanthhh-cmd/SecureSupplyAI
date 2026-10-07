from typing import List, Dict, Any

POPULAR_PACKAGES = {
    "PyPI": [
        "requests", "urllib3", "pip", "setuptools", "wheel", "pytest", "numpy",
        "pandas", "scipy", "scikit-learn", "flask", "django", "pillow", "boto3",
        "pyyaml", "cryptography", "sqlalchemy", "torch", "tensorflow"
    ],
    "npm": [
        "react", "react-dom", "express", "lodash", "axios", "typescript",
        "webpack", "next", "vue", "moment", "chalk", "commander", "debug",
        "fs-extra", "async", "core-js", "dotenv"
    ],
    "Maven": [
        "org.springframework.boot:spring-boot-starter-web",
        "org.apache.logging.log4j:log4j-core",
        "org.slf4j:slf4j-api",
        "com.fasterxml.jackson.core:jackson-databind",
        "org.junit.jupiter:junit-jupiter-api",
        "org.mockito:mockito-core"
    ]
}

def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class AttackDetectionEngine:
    @staticmethod
    def detect_typosquatting(package_name: str, ecosystem: str) -> List[Dict[str, Any]]:
        indicators = []
        pkg_lower = package_name.lower()
        targets = POPULAR_PACKAGES.get(ecosystem, []) + POPULAR_PACKAGES["PyPI"] + POPULAR_PACKAGES["npm"]

        for target in targets:
            target_lower = target.lower()
            if pkg_lower == target_lower:
                continue
            
            dist = levenshtein_distance(pkg_lower, target_lower)
            if dist == 1 or (dist == 2 and len(pkg_lower) >= 6):
                indicators.append({
                    "dependency_name": package_name,
                    "attack_type": "Typosquatting",
                    "severity": "HIGH",
                    "description": f"Package '{package_name}' closely resembles popular package '{target}' (Levenshtein edit distance: {dist})",
                    "evidence": {
                        "target_package": target,
                        "distance": dist,
                        "ecosystem": ecosystem
                    }
                })
                break
        return indicators

    @staticmethod
    def detect_dependency_confusion(package_name: str, ecosystem: str) -> List[Dict[str, Any]]:
        indicators = []
        pkg_lower = package_name.lower()

        # Check internal patterns
        internal_prefixes = ["@internal/", "corp-", "internal-", "company-", "private-"]
        if any(pkg_lower.startswith(prefix) for prefix in internal_prefixes):
            indicators.append({
                "dependency_name": package_name,
                "attack_type": "Dependency Confusion",
                "severity": "CRITICAL",
                "description": f"Package '{package_name}' matches internal corporate naming pattern but was resolved from public registry",
                "evidence": {
                    "package_name": package_name,
                    "naming_pattern": "Internal corporate prefix detected",
                    "risk": "Potential public registry substitution attack"
                }
            })
        return indicators

    @staticmethod
    def detect_package_takeover(package_name: str, suspicion_score: float, suspicious_reasons: List[str]) -> List[Dict[str, Any]]:
        indicators = []
        if suspicion_score >= 50.0 and any("KNOWN_SUSPICIOUS_PACKAGE" in r or "SUSPICIOUS_NAME" in r for r in suspicious_reasons):
            indicators.append({
                "dependency_name": package_name,
                "attack_type": "Package Takeover",
                "severity": "CRITICAL",
                "description": f"Package '{package_name}' exhibits maintainer anomaly or hijacked release indicators",
                "evidence": {
                    "suspicion_score": suspicion_score,
                    "reasons": suspicious_reasons
                }
            })
        return indicators

    @staticmethod
    def detect_malicious_updates(package_name: str, suspicious_reasons: List[str]) -> List[Dict[str, Any]]:
        indicators = []
        network_reasons = [r for r in suspicious_reasons if "SUSPICIOUS_NETWORK" in r or "SHELL_EXEC" in r]
        if network_reasons:
            indicators.append({
                "dependency_name": package_name,
                "attack_type": "Malicious Update",
                "severity": "CRITICAL",
                "description": f"Package '{package_name}' contains suspicious shell execution or exfiltration hooks inserted into release",
                "evidence": {
                    "reasons": network_reasons
                }
            })
        return indicators

    @classmethod
    def analyze_all_attacks(cls, package_name: str, ecosystem: str, suspicion_score: float, suspicious_reasons: List[str]) -> List[Dict[str, Any]]:
        all_indicators = []
        all_indicators.extend(cls.detect_typosquatting(package_name, ecosystem))
        all_indicators.extend(cls.detect_dependency_confusion(package_name, ecosystem))
        all_indicators.extend(cls.detect_package_takeover(package_name, suspicion_score, suspicious_reasons))
        all_indicators.extend(cls.detect_malicious_updates(package_name, suspicious_reasons))
        return all_indicators
