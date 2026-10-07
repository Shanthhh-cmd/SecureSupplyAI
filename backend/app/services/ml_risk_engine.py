import os
import joblib
import numpy as np
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("securesupply.ml_risk")

MODEL_PATH = "/home/tracehanami/Github/SecureSupplyAI/backend/app/ml/risk_model.joblib"

class MLRiskEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Loaded Random Forest model from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")

    def calculate_risk(
        self,
        vulnerabilities: List[Dict[str, Any]],
        suspicion_score: float,
        attack_indicators: List[Dict[str, Any]],
        total_dependencies: int,
        transitive_count: int
    ) -> Dict[str, Any]:
        
        vuln_count = len(vulnerabilities)
        max_cvss = max([v.get("cvss_score", 0.0) for v in vulnerabilities], default=0.0)
        critical_count = sum(1 for v in vulnerabilities if v.get("severity") == "CRITICAL")
        high_count = sum(1 for v in vulnerabilities if v.get("severity") == "HIGH")
        attack_flag = 1 if len(attack_indicators) > 0 else 0
        transitive_ratio = (transitive_count / max(total_dependencies, 1))
        popularity = 0.8 # baseline popularity assumption

        # Feature vector for ML model
        features = np.array([[
            vuln_count,
            max_cvss,
            critical_count,
            high_count,
            suspicion_score,
            attack_flag,
            transitive_ratio,
            popularity
        ]])

        # Rule-based fallback & raw score computation (0 - 100)
        raw_score = (
            (max_cvss * 5.5) +
            (critical_count * 15.0) +
            (high_count * 8.0) +
            (suspicion_score * 0.35) +
            (attack_flag * 30.0) +
            (transitive_ratio * 5.0)
        )
        overall_score = round(float(np.clip(raw_score, 0.0, 100.0)), 1)

        predicted_level = "Low"
        if self.model:
            try:
                pred = self.model.predict(features)[0]
                predicted_level = str(pred)
            except Exception as e:
                logger.warning(f"ML model prediction error: {e}")
        
        # Override rules for safety
        if overall_score >= 70.0 or attack_flag == 1 or critical_count >= 2:
            predicted_level = "Critical"
        elif overall_score >= 45.0 or high_count >= 2 or suspicion_score >= 50.0:
            predicted_level = "High"
        elif overall_score >= 20.0 or vuln_count >= 1:
            predicted_level = "Medium"
        else:
            predicted_level = "Low"

        vulnerability_score = round(min((max_cvss * 7.0) + (critical_count * 10), 100.0), 1)
        reputation_score = round(max(100.0 - (suspicion_score * 1.2), 0.0), 1)

        return {
            "overall_score": overall_score,
            "risk_level": predicted_level,
            "vulnerability_score": vulnerability_score,
            "suspicion_score": round(suspicion_score, 1),
            "reputation_score": reputation_score,
            "feature_breakdown": {
                "vuln_count": vuln_count,
                "max_cvss": max_cvss,
                "critical_count": critical_count,
                "high_count": high_count,
                "suspicion_score": suspicion_score,
                "attack_indicators_count": len(attack_indicators),
                "transitive_ratio": round(transitive_ratio, 2)
            },
            "ml_model_version": "1.0.0-random-forest"
        }

ml_risk_engine = MLRiskEngine()
