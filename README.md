# Pharmacy IV Cleanroom USP 797

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** USP <797> Pharmaceutical Compounding, CAP / CLSI / ISO Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Pharmacy IV Cleanroom USP 797 is an enterprise-grade clinical decision support system for sterile compounding cleanroom environment monitoring and beyond-use-date (BUD) compliance. It provides:

- **Multi-Agent Evaluation Engine**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate task payloads against clinical thresholds
- **USP-797 Sentinel**: Dedicated subsystem for ISO Class 5/7/8 environmental monitoring, pressure differentials, and BUD calculations
- **Enrichment Suite**: 8 domain-specific engines for media fill documentation, hazardous drug handling, staff training, and quality assurance
- **Tamper-Evident Audit Trail**: HMAC-SHA256 chained cryptographic audit logs for every evaluation
- **Zero-PHI Outbound Guard**: Active pattern detection blocking SSNs, MRNs, phone numbers, and patient identifiers

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with USP <797> formulations and thresholds
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated clinical/operational action recommendations
- **Validation & Guardrails**: Rigorous input bounds checking, finite number validation, and control character injection prevention
- **Prometheus Telemetry**: Operational metrics export for monitoring
- **Active Learning Calibration**: Bayesian worker reliability weight tracking

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/pharmacy-iv-cleanroom-usp-797.git
cd pharmacy-iv-cleanroom-usp-797

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Optional: Set audit secret key for persistent audit integrity
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. System Configuration Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (required, max 128 chars)
- `--target`: Entity or target identifier (required, max 128 chars)
- `--primary`: Primary domain measurement (float, finite)
- `--secondary`: Secondary kinetic/confidence score (float, finite)
- `--critical`: Emergency escalation flag (boolean)
- `--status`: Status code or phenotype descriptor (max 64 chars)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required, max 128 chars |
| `target_identifier` | Entity or target identifier | Required, max 128 chars |
| `primary_metric` | Primary domain measurement | Required, finite float |
| `secondary_metric` | Secondary kinetic score | Optional, finite float |
| `is_critical_flag` | Emergency escalation trigger | Optional, boolean |
| `status_descriptor` | Status code or phenotype | Optional, max 64 chars |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB patterns, and patient identifiers
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with full signature verification for every evaluation
* **Input Validation:** Pydantic v2 models with field validators preventing control character injection and ensuring finite numeric values
* **Secure Defaults:** Ephemeral key generation when AUDIT_SECRET_KEY is not set (with warning)
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`)

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t pharmacy-iv-cleanroom-usp-797 .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key pharmacy-iv-cleanroom-usp-797
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
pharmacy-iv-cleanroom-usp-797/
├── agents/                      # Main multi-agent evaluation system
│   ├── __init__.py
│   ├── api.py                   # FastAPI REST server
│   ├── base.py                  # Security, PHI guard, HMAC audit trail
│   ├── learning.py              # Bayesian calibration engine
│   ├── llm_factory.py           # LLM provider factory
│   ├── metrics.py               # Prometheus metrics collector
│   ├── models.py                # Pydantic v2 data models
│   ├── streamer.py              # WebSocket telemetry broadcaster
│   ├── supervisor.py            # Master orchestrator
│   └── workers.py               # Specialized evaluation workers
├── usp_797_cleanroom/           # USP-797 Sentinel subsystem
│   ├── __init__.py
│   ├── agents.py                # Sub-agents (DifferentialPressure, AirParticleCount, BeyondUseDate)
│   ├── cli.py                   # CLI for USP-797 subsystem
│   ├── engine.py                # Core algorithmic engine
│   ├── models.py                # Dataclass models with validation
│   └── server.py                # FastAPI server factory
├── tests/                       # Pytest test suite
│   ├── test_pharmacy_iv_cleanroom_usp_797.py
│   ├── test_usp_797_cleanroom.py
│   └── test_enrichment.py
├── web/                         # Operations console (HTML/JS)
├── cli.py                       # Main CLI entry point
├── enrichment.py                # 8 domain-specific enrichment engines
├── simulator.py                 # High-throughput stress testing
├── pyproject.toml               # Project metadata and dependencies
├── Dockerfile                   # Container build instructions
├── docker-compose.yml           # Multi-container orchestration
└── .github/workflows/ci.yml     # CI/CD pipeline
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
