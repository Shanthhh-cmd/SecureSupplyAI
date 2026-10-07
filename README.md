# SecureSupply AI — Software Supply Chain Security Platform

**SecureSupply AI** is a production-grade Software Supply Chain Security Platform designed to help developers, security engineers, and organizations identify vulnerable, malicious, outdated, or suspicious software dependencies before they are deployed into production environments.

---

## 🌟 Key Features & Functional Modules

### 1. Project Intake & Ingestion Engine
- **Source Code ZIP Archives**: Extract and analyze compressed source repositories.
- **Manifest Ingestion**: Parse `requirements.txt` (Python pip), `package.json` (JavaScript npm), `pom.xml` (Java Maven).
- **Software Bill of Materials (SBOM)**: Direct parsing and generation of **CycloneDX 1.4 JSON** format.
- **Git Repository Integration**: Direct cloning and automated scanning of public or private Git URLs.

### 2. Dependency Discovery Engine
- **Direct & Transitive Dependency Resolution**: Unpack full dependency trees.
- **Ecosystem Support**: Python (PyPI), JavaScript (npm), Java (Maven).
- **License Identification**: Detect license types and compliance flags.

### 3. Vulnerability Intelligence & Assessment
- Integration with **OSV.dev**, **National Vulnerability Database (NVD)**, and **GitHub Security Advisories**.
- Match dependencies against CVE identifiers, CVSS v3 scores, severity levels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), and remediation versions.
- Offline fallback vulnerability database for deterministic, high-speed scan execution.

### 4. Suspicious Package Static Analysis
- **Obfuscation Detection**: Flag `eval(base64)`, `exec(zlib)`, hex-encoded byte payloads, dynamic builtin imports.
- **Excessive Shell Execution**: Detect `subprocess.Popen(shell=True)`, `os.system`, `child_process.exec`, `Runtime.exec`.
- **Install Script Hooks**: Detect `postinstall` shell scripts, `preinstall` downloaders, custom `setup.py` overrides.
- **Exfiltration & Network Indicators**: Hardcoded IPv4 target addresses, Discord webhook exfiltration endpoints, raw TCP sockets.
- **Suspicion Score Calculation**: 0.0 to 100.0 numerical score with explicit trigger rationale.

### 5. Supply Chain Attack Detection Engine
- **Typosquatting**: Damerau-Levenshtein distance matching against popular Python, npm, and Maven package registries.
- **Dependency Confusion**: Internal corporate naming pattern checks (`@internal/`, `corp-`, `company-`) resolved from public registries.
- **Package Takeover**: Maintainer anomaly and hijacked package release detection.
- **Malicious Updates**: Detection of network exfiltration script insertions in package diffs.

### 6. Random Forest Machine Learning Risk Engine
- **Scikit-learn Random Forest Model**: Predicts risk levels (`Low`, `Medium`, `High`, `Critical`) and calculates overall risk scores (0–100).
- Multi-factor evaluation: Vulnerability count, Max CVSS, Critical/High counts, Suspicion score, Attack flags, Transitive ratios, Popularity metrics.

### 7. Automated Security Policy Engine
- Configurable organization rules: Maximum allowed CVSS score, Risk score threshold, Suspicion score cap, Typosquatting block toggle, Blacklisted package enforcement.
- Enforced actions: `ALLOW`, `WARN`, `RECOMMEND_UPDATE`, `QUARANTINE`, `BLOCK`.

### 8. Recommendation & Remediation Guidance
- Actionable steps: `UPGRADE`, `DOWNGRADE`, `REPLACE`, `REMOVE`, `PATCH`.
- Rationale generation for every finding.

### 9. Interactive Cybersecurity Dashboard
- **Executive Summary**: Real-time metrics for total dependencies, vulnerable packages, critical findings, blocked dependencies.
- **Recharts Visualizations**: Vulnerability severity pie chart, Risk level distribution, Scan history risk timelines.
- **Exploration Tables**: Dependency inventory, Vulnerabilities, Attack indicators, Policy decisions, CycloneDX SBOM explorer.

### 10. Multi-Format Report Exporter
- Downloadable **PDF Reports** (via ReportLab).
- Downloadable **JSON Reports** & **CSV Inventory Spreadsheets**.

---

## 🏗️ Architecture Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Alembic, Scikit-learn, Pandas, NumPy, ReportLab, PyJWT, Bcrypt.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts, React Router.
- **Database**: PostgreSQL (Production) / SQLite (Development).
- **Containerization**: Docker, Docker Compose, Nginx.

---

## 🚀 Quick Start & Installation

### Option 1: Running Locally (Development Mode)

#### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Train the Random Forest Risk Model
python app/ml/train_model.py

# Start FastAPI Server
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```
- API Documentation: `http://localhost:8000/docs`
- Default Admin Credentials: `admin@securesupply.ai` / `admin123`

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:5173` in your browser.

---

### Option 2: Docker Compose Deployment

```bash
docker-compose up --build -d
```
- Frontend Web App: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Database: `localhost:5432`

---

## 🧪 Running Tests

```bash
cd backend
PYTHONPATH=. venv/bin/pytest tests/
```

---

## 📄 License
Released under the MIT License. Developed for Enterprise Supply Chain Security & Defense Demonstration.
