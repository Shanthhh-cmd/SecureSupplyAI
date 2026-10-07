import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def generate_synthetic_dataset(samples=2000):
    np.random.seed(42)
    
    # Feature 0: vuln_count
    vuln_count = np.random.poisson(lam=1.5, size=samples)
    
    # Feature 1: max_cvss
    max_cvss = np.where(vuln_count > 0, np.random.uniform(2.0, 10.0, size=samples), 0.0)
    
    # Feature 2: critical_count
    critical_count = np.where(max_cvss >= 9.0, np.random.randint(1, 4, size=samples), 0)
    
    # Feature 3: high_count
    high_count = np.where((max_cvss >= 7.0) & (max_cvss < 9.0), np.random.randint(1, 4, size=samples), 0)
    
    # Feature 4: suspicion_score (0 - 100)
    suspicion_score = np.random.exponential(scale=10.0, size=samples)
    suspicion_score = np.clip(suspicion_score, 0.0, 100.0)
    
    # Feature 5: attack_indicator_flag (0 or 1)
    attack_flag = np.random.choice([0, 1], p=[0.85, 0.15], size=samples)
    
    # Feature 6: transitive_ratio (0.0 - 1.0)
    transitive_ratio = np.random.beta(a=2, b=2, size=samples)
    
    # Feature 7: popularity_index (0.0 - 1.0, 1 = super popular)
    popularity = np.random.uniform(0.1, 1.0, size=samples)

    X = np.column_stack([
        vuln_count,
        max_cvss,
        critical_count,
        high_count,
        suspicion_score,
        attack_flag,
        transitive_ratio,
        popularity
    ])

    # Target calculation rule to generate ground truth classification
    risk_labels = []
    for row in X:
        v_cnt, cvss, crit, high, susp, att, trans, pop = row
        
        score = (
            (cvss * 6) +
            (crit * 15) +
            (high * 8) +
            (susp * 0.4) +
            (att * 25) +
            (trans * 5) -
            (pop * 5)
        )
        
        if score >= 65 or att == 1 or crit >= 2:
            risk_labels.append("Critical")
        elif score >= 40 or high >= 2 or susp >= 50:
            risk_labels.append("High")
        elif score >= 20 or v_cnt >= 2:
            risk_labels.append("Medium")
        else:
            risk_labels.append("Low")

    y = np.array(risk_labels)
    return X, y

def train_and_save_model(output_path="/home/tracehanami/Github/SecureSupplyAI/backend/app/ml/risk_model.joblib"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    X, y = generate_synthetic_dataset()
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X, y)
    
    joblib.dump(clf, output_path)
    print(f"Random Forest ML risk model trained and saved to {output_path}")

if __name__ == "__main__":
    train_and_save_model()
