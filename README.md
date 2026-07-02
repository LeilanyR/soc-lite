# SOC-Lite

A lightweight Security Operations Center (SOC) that ingests AWS CloudTrail logs, detects attack patterns using custom detection rules, and generates security alerts — with a live web dashboard.

🔗 **[Live Dashboard](https://leilanyr.github.io/soc-lite/)**

## What It Does

SOC-Lite simulates how a real SIEM (Security Information and Event Management) tool works:

1. **Ingests** raw AWS CloudTrail logs
2. **Normalizes** events into a searchable database
3. **Detects** threats using config-driven YAML rules
4. **Alerts** with severity-ranked findings
5. **Visualizes** results on a web dashboard

## Attack Scenario Detected

The included dataset simulates a real cloud attack kill chain:

| Phase | What Happens | MITRE ATT&CK |
|-------|-------------|---------------|
| Reconnaissance | Attacker lists S3 buckets, objects, and security groups | [T1580 - Cloud Infrastructure Discovery](https://attack.mitre.org/techniques/T1580/) |
| Credential Discovery | Attacker enumerates key pairs and compute resources | [T1580 - Cloud Infrastructure Discovery](https://attack.mitre.org/techniques/T1580/) |
| Privilege Escalation | EC2 instance assumes an unauthorized IAM role | [T1078 - Valid Accounts](https://attack.mitre.org/techniques/T1078/) |
| Exfiltration | Attacker downloads sensitive file from S3 | [T1530 - Data from Cloud Storage](https://attack.mitre.org/techniques/T1530/) |

## Detection Rules

Rules are defined in YAML — no code changes needed to add new detections:

**Critical/High:**
- **Rapid Role Assumption** (CRITICAL) — Multiple role assumptions in a short time window
- **S3 Data Exfiltration** (HIGH) — Assumed role downloads an S3 object
- **Privilege Escalation via Role Assumption** (HIGH) — Service assumes IAM role
- **Rapid S3 Enumeration** (HIGH) — Multiple S3 list operations in a short time window

**Medium:**
- **S3 Bucket Enumeration** (MEDIUM) — Lists all buckets (active recon)
- **S3 Object Enumeration** (MEDIUM) — Lists files inside a bucket (active recon)
- **Credential Discovery** (MEDIUM) — Lists key pairs (looking for SSH access)

**Low:**
- **Unusual Reconnaissance Activity** (LOW) — Describes security groups (network mapping)
- **EC2 Instance Discovery** (LOW) — Describes EC2 instances (mapping compute)
- **Storage Reconnaissance** (LOW) — Describes EBS volumes (mapping data storage)

## How To Run

```bash
# 1. Clone the repo
git clone https://github.com/LeilanyR/soc-lite.git
cd soc-lite

# 2. Install dependencies
pip install pyyaml

# 3. Ingest logs into database
python src/main.py

# 4. Run detection rules
python src/detector.py

# 5. Launch dashboard
python src/dashboard.py
# Open http://localhost:8080/index.html

Architecture

CloudTrail Logs (JSON) → Parser → SQLite Database → Detection Engine → Alerts → Dashboard

Tech Stack

- Python — log parsing, detection engine, alerting
- SQLite — event storage and querying
- YAML — config-driven detection rules
- HTML/CSS/JS — web dashboard with dark theme and 3D effects

Data Sources

CloudTrail logs sourced from the OTRF Security Datasets (https://github.com/OTRF/Security-Datasets) project (MIT License) — simulated attack scenarios for security research and detection development.

Also — add `*.db` to your `.gitignore` and remove the database from git:

```bash
git rm --cached soc_lite.db