#  SOC-Lite

A lightweight Security Operations Center that ingests AWS CloudTrail logs, detects attack patterns using custom rules, and generates security alerts.

## Data Sources

CloudTrail logs sourced from the [OTRF Security Datasets](https://github.com/OTRF/Security-Datasets) project (MIT License) — simulated attack scenarios for security research and detection development.

## Setup

```bash
python src/main.py