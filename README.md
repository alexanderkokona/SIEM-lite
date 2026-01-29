# Auth Log Security Pipeline

This project builds a small, disciplined security log pipeline starting with
Linux authentication logs (`auth.log`). The goal is to ingest, parse, and
analyze authentication events in a way that mirrors real SOC workflows.

The project emphasizes:
- Correct log access and permissions
- Reliable ingestion and parsing
- Clear event schemas
- Detection logic that is explainable and testable

This is **not** a dashboard-first or ML-first project. Everything builds on
verified data access and structured events.

---

## Current Scope (Sprint 1)

Sprint 1 focuses only on:
- Verifying access to `auth.log`
- Reading logs safely and consistently
- Establishing configuration-driven log sources

No detection logic, alerts, or dashboards are implemented yet.

---

## Data Source

- Primary source: `/var/log/auth.log`
- Platform: Linux (Debian/Ubuntu-style logging)
- Log rotation is expected and handled later

---

## How to Run (for now)

```bash
python scripts/verify_auth_log_access.py
