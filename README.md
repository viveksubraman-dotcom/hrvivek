# Enterprise HR Agentic Solution (MVP 1)

Enterprise-grade conversational AI virtual assistant for HR and IT services, grounded in the **Google Cloud Architecture Framework (Well-Architected 6 Pillars)**, **Google Secure AI Framework (SAIF)**, and **Open Knowledge Format (OKF)**.

## Architecture Highlights
- **Layer 2 (Zero-Trust Security)**: In-process heuristic regex pre-scan (<15ms) for prompt injection and out-of-scope defense; OIDC/IAP user claims validator; SPII masking.
- **Layer 3 (Agent Core & Validation)**: Deterministic validation middleware (balance calculation, temporal sanity, phone E.164 syntax, ticket lifecycle state machine); durable distributed Saga coordinator with 2-phase commit and compensating rollback.
- **Layer 4 (Connectors & OKF Brain)**: WorkWeek HCM connector; ServiceImmediately ITSM connector with 5-minute anti-duplicate window; OKF Tri-Hybrid Search Brain with deep-link source citations (`POL-SG-2026-V1#sec-XX`).

## 43-Scenario Benchmark Suite
Run the full 43-case evaluation test suite:
```bash
uv run pytest -v
```
