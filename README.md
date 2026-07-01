# 🚀 ARTEMIS Sentinel — AI-RPA Mission Validation System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![NASA API](https://img.shields.io/badge/NASA%20API-DONKI%20%26%20POWER-red.svg)](https://api.nasa.gov/)
[![Tests](https://img.shields.io/badge/tests-Pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![RPA](https://img.shields.io/badge/RPA-Autonomous%20Validation-FF6F61.svg)](#)
[![Dashboard](https://img.shields.io/badge/dashboard-Streamlit-FF4B4B.svg)](https://streamlit.io/)

> **Ensuring mission compliance and operational safety through autonomous robotic process automation and local intelligence.**

ARTEMIS Sentinel is an enterprise-grade AI-RPA system designed to validate simulated lunar missions. By integrating real-time telemetry ingestion, live NASA climate and space weather APIs, local Machine Learning risk engines, and robust fallback pipelines, ARTEMIS Sentinel provides flight directors with a complete verification suite for mission critical safety checks.

---

## 🛰️ Key Highlights

- **Autonomous Fallback Pipeline:** Intelligent, self-healing data collectors for NASA POWER and NASA DONKI APIs that automatically switch to high-fidelity local fallback datasets in case of rate limits or connection disruptions.
- **Local ML Risk Modeling:** Integrates a local `IsolationForest` anomaly detector to isolate multi-variable telemetry deviations, backed by a statistical Z-score baseline engine for cross-validation.
- **Hierarchical Risk Matrix:** Advanced rule-based validation module mapping operational metrics (oxygen levels, battery capacity, cabin pressure, signal latency) to high-impact alert statuses (`GO`, `GO WITH CAUTION`, `WARNING`, `NO-GO`).
- **Enterprise Reporting:** Automated multi-sheet Excel generation (`openpyxl`) paired with SMTP email delivery mechanisms, generating auditable validation run documents.
- **Real-Time Streamlit Dashboard:** An interactive control console displaying real-time telemetry timelines, mission risk scores, active warning alerts, and conceptual 2D Earth-to-Moon flight progress.

---

## 🏗️ Architecture Layout

```text
artemis-sentinel/
├── main.py                    # CLI Entrypoint
├── app.py                     # Streamlit Operational Console
├── requirements.txt           # Dependency Manifest
├── pytest.ini                 # Pytest Configuration
├── .env.example               # Environment Template
├── .gitignore                 # Version Control Ignore Files
│
├── data/
│   ├── fallback/              # Local High-Fidelity JSON Fallbacks
│   ├── raw/                   # Raw Ingested Mission Artifacts
│   ├── processed/             # Cleaned Telemetry Records
│   └── reports/               # Generated Excel Run Sheets
│
├── database/                  # SQLite Database Storage
├── logs/                      # System Log Registry
│
├── src/
│   ├── collectors/            # NASA API Ingestion Handlers
│   ├── telemetry/             # Synthetic Telemetry Simulators
│   ├── intelligence/          # Anomaly Detectors & Risk Matrices
│   ├── notifications/         # SMTP Notification Modules
│   ├── reports/               # Excel Document Builders
│   ├── utils/                 # Path & DateTime Helpers
│   ├── config.py              # Configuration & Security Engine
│   └── database.py            # SQLite ORM & Persistence Layer
│
└── tests/                     # Security & Validation Tests Suite
```

---

## 🖥️ Streamlit Dashboard Preview

Below is a conceptual layout of the **ARTEMIS Sentinel Dashboard**:

```html
+---------------------------------------------------------------------------------+
| [🪐 ARTEMIS Sentinel]             NASA API Status: [REAL_CONFIGURED]            |
+---------------------------------------------------------------------------------+
| CONFIGURATION:                                                                  |
|   Telemetry Samples: [=========o=========] 120                                  |
|   [x] Enable Anomaly Mode                     [ EXECUTE MISSION VALIDATION ]   |
+---------------------------------------------------------------------------------+
| MISSION SUMMARY                                                                 |
| +------------------+ +------------------+ +------------------+ +-------------+ |
| | Mission Status   | | Risk Level       | | Critical Alerts  | | Data Mode   | |
| |       GO         | |      LOW         | |       0        | | NASA LIVE   | |
| +------------------+ +------------------+ +------------------+ +-------------+ |
|                                                                                 |
| CONCEPTUAL TRAJECTORY (EARTH -> MOON)                                           |
|   Earth [O]-----------------------------[🚀 Craft]-----------------------[o] Moon|
|   Telemetry Info: min=120 | battery=94% | oxygen=98% | latency=10ms             |
|                                                                                 |
| TELEMETRY TIMELINES                                                             |
|   100% |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ (Battery)            |
|    50% |                                                                        |
|     0% +--------------------------------------------------                      |
|                                                                                 |
| ML ANOMALY ENGINE                                                               |
|   Anomaly Ratio: 0.00%  |  IsolationForest Estimators: 100                      |
+---------------------------------------------------------------------------------+
```

---

## 🚀 Local Installation & Setup

Follow these clean steps to deploy ARTEMIS Sentinel locally:

### 1. Clone the Repository
```bash
git clone https://github.com/fecabrall/artemis-sentinel.git
cd artemis-sentinel
```

### 2. Configure Virtual Environment
Create a localized Python sandbox environment:

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Secrets & Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
Open `.env` and fill in your settings:
```env
NASA_API_KEY=DEMO_KEY           # Replace with your NASA API Key (https://api.nasa.gov/)
EMAIL_ENABLED=false             # Set to true to enable email summary alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_APP_PASSWORD=              # Google App Password (16 characters)
ALERT_EMAIL_TO=recipient@mail.com
SEND_EXCEL_ATTACHMENT=false
```

---

## 🔐 NASA_API_KEY Security & Secret Handling
- **Never commit active API keys to public repositories.**
- To run the application in demonstration mode, keep `NASA_API_KEY=DEMO_KEY`.
- If you accidentally commit a real key, **revoke** and regenerate it immediately.

---

## 🛠️ Usage Instructions

### Run CLI Pipeline Validation
Run the core pipeline directly in the terminal:
```bash
# Normal simulated flight path
python main.py

# Simulate critical failures / orbital hazards
python main.py --anomaly
```

### Start Streamlit Control Dashboard
Fire up the web console to view plots, trajectories, and trigger operational summaries:
```bash
streamlit run app.py
```

### Run Safety & Functional Tests
Validate code behavior, regression parameters, and secret masking rules:
```bash
python -m pytest -v
```

---

## 👤 Author

Developed and maintained by **Felipe Cabral**. Let's connect!

- **LinkedIn:** [Felipe Cabral](https://www.linkedin.com/in/fecabrall/)
- **GitHub:** [@fecabrall](https://github.com/fecabrall)

---

## 📄 License
This project is released under the **MIT License**. See `LICENSE` for details.
