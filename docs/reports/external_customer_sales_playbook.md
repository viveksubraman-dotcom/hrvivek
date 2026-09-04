# External Customer Sales Playbook: Autonomous Enterprise HR Operations

**Version:** 7.5 (Refined 9-Slide Enterprise Delivery • Unified Design Standard)  
**Target Audience:** Enterprise C-Suite Buying Committee (Executive Officer / CEO, Chief Procurement Officer, Chief Digital Officer, Enterprise Architect, Security Architect / CISO, Chief HR Officer)  
**Pitch Duration:** 15 Minutes (9 Refined Master Slides)  
**Design Standard:** Minimalist Enterprise Slate (Tailwind CSS, Unified Dual-Accent Palette, Zero Meta Clutter, High-Contrast Typography)  
**Core Value Levers:** $540,000 Year 1 Net Savings (&ge;40% Deflection) • Scaling to $2.04M at Enterprise Maturity (85%) • &lt;3.5s MTTR • Deterministic Policy Guardrails (99.8% Grounded Truth)  

---

## 1. Executive Summary & Core Grounding

This playbook governs the delivery of the 15-minute executive sales keynote for the **Autonomous Enterprise HR Operations Platform**. Every metric, logical architecture tier, and policy rule is strictly anchored in the Business Requirements Document (`docs/brd/BRD_MVP1.md`), the Customer Design Blueprint (`docs/reports/design_blueprint.md`), and the verified codebase (`https://github.com/CHOLHOJONG/my-agent.git`).

### Grounded Commercial & Architectural Fundamentals
1. **Grounded Unit Economics:** Anchored in BRD Table 1.1.1 baseline of 12,500 monthly Tier-1 tickets ($150,000/mo direct labor cost across 18 FTEs @ $12/ticket). Delivering **$540,000 in Year 1 net savings** at &ge;40% initial deflection ($45,000/month net), scaling to **$2.04M annual net value** at mature 85% deflection across 10,000 employees.
2. **Operational Acceleration:** Slashes Mean Time to Resolution (MTTR) from 48–72 hours down to **under 3.5 seconds** with sub-second Time-to-First-Token (TTFT).
3. **Refined 9-Slide Delivery Choreography:**
   - **Slide 1: Current State Baseline (Before)** — Leads with commercial friction, ticket volumes, and financial bleed.
   - **Slide 2: Target Outcomes (After) & Live ROI Engine** — Immediate contrast presenting target outcomes, deflection targets, and the live interactive ROI calculator.
   - **Slide 3: Solution Scope & Operational Boundary** — Establishes strict service boundaries across 4 core high-volume workflows.
   - **Slide 4: Business Requirements Traceability** — Pure BRD traceability (FR-1 to FR-5, NFR-1 to NFR-4, Section 7 benchmarks).
   - **Slide 5: Logical Architecture & MCP Decoupling** — 6-tier systems architecture detailing the exact functional role of each tier from `design_blueprint.md` and SDD Block 0.
   - **Slide 6: The OKF Tri-Hybrid Brain** — Dense vector (`text-embedding-004`), lexical BM25, and deterministic rule graphs fused via Reciprocal Rank Fusion ($RRF\ k=60$) enforcing concrete policies (`POL-HR-04`, `POL-HR-08`, `POL-HR-01`, `POL-EXP-01`) and kinship rules (5 days immediate vs 3 days extended; pet bereavement routed to PTO).
   - **Slide 7: Enterprise Security & Data Governance** — Zero-Trust Google SAIF, Cloud IAP edge authentication, OIDC JWKS token verification, sub-15ms heuristic pre-scan (0.04ms actual), Cloud KMS CMEK encryption, in-memory DLP, and contractual zero data retention.
   - **Slide 8: Phased Adoption Roadmap** — Week 3 Champions (100) $\rightarrow$ Week 4 Feedback Pilot (1,000) $\rightarrow$ Enterprise Scale (10,000).
   - **Slide 9: Strategic Summary & Next Steps** — Immediate 14-day sandbox pilot authorization under $150/month zero-CapEx budget allocation.
4. **Deterministic Policy Guardrails (Non-Stochastic Grounding):** Large language models are probabilistic. Hallucination risk is eliminated through deterministic Python validation middleware (`app/middleware/validation.py`) and Open Knowledge Format (OKF) Rule Graphs (`app/brain/policies.py`).
5. **Model Context Protocol (MCP) Decoupling:** Implemented in `app/connectors/mcp_saas.py`, the agent communicates via JSON-RPC 2.0 with dynamic bearer token injection from Secret Manager (`X-MCP-Token`). Model prompts remain 100% untouched even if backends swap between ServiceNow, Jira, Workday, or SAP.

---

## 2. 15-Minute 9-Slide Delivery Choreography & Talk Tracks

```
[00:00 - 01:30] Slide 1:  Current State Baseline — Before (12,500 tickets/mo, 48-72h MTTR, $150k/mo Labor, 14.5% Re-Open)
[01:30 - 03:15] Slide 2:  Target Outcomes (After) & Live ROI Engine (>=40% Deflection, <3.5s MTTR, $540k/yr Savings)
[03:15 - 04:45] Slide 3:  Solution Scope & Operational Boundary (Tier 1 Deflection, Knowledge, Equipment, Leave Sagas)
[04:45 - 06:15] Slide 4:  Requirements Traceability: Pure BRD (FR-1 to FR-5, NFR-1 to NFR-4, Section 7 Benchmarks)
[06:15 - 08:30] Slide 5:  Logical Architecture: 6-Tier Enterprise Systems Topology & Tier Responsibilities
[08:30 - 10:15] Slide 6:  The OKF Tri-Hybrid Brain: Eliminating Policy Hallucination (Vector + BM25 + Rule Graph, RRF k=60)
[10:15 - 11:45] Slide 7:  Security & Governance: Google SAIF, Zero-Trust IAP, Cloud KMS CMEK & Zero Retention
[11:45 - 13:15] Slide 8:  Adoption Roadmap: From Week 3 Champions to 10,000 Users (100 -> 1k -> 10k Enterprise Scale)
[13:15 - 15:00] Slide 9:  Strategic Summary & Next Steps: Immediate 14-Day Pilot Authorization (<$150/mo Sandbox Budget)
```

### Detailed Slide Delivery Guide

#### 🎯 Slide 1: Current State Baseline — Before (00:00 - 01:30)
- **Visual Focus:** Red-accented friction cockpit detailing 12,500 monthly tickets, 48–72h MTTR, $150,000/mo labor bleed, and 14.5% re-open rate.
- **Presenter Script:** *"Members of the executive committee: every month, 12,500 routine tier-1 HR and IT tickets flood our helpdesk. Our employees wait 48 to 72 hours for basic answers regarding leave entitlements, equipment stipends, or relocation rules. That delay costs us $150,000 every single month in dedicated support labor across 18 FTEs. Worse, 14.5% of tickets are re-opened due to inconsistent manual interpretation. This friction is dragging down employee productivity and draining our operating budget."*

#### 🎯 Slide 2: Target Outcomes (After) & Live ROI Engine (01:30 - 03:15)
- **Visual Focus:** Emerald-accented target outcomes panel paired with the live interactive ROI calculator.
- **Presenter Script:** *"Here is the future we have engineered. By deploying Elevate HR, we slash Mean Time to Resolution from 72 hours to under 3.5 seconds. In Year 1, an initial 40% deflection rate automates 5,000 tickets monthly, capturing $540,000 in direct net cash savings ($45,000/month). As shown in our live ROI engine, scaling to enterprise maturity across 10,000 employees at 85% deflection unlocks $2,040,000 in recurring net annual value. Re-open rates plummet from 14.5% to under 2.0% because answers are deterministically grounded in approved policy."*

#### 🎯 Slide 3: Solution Scope & Operational Boundary (03:15 - 04:45)
- **Visual Focus:** 4 functional quadrants: Tier 1 Deflection, Knowledge Synthesis, Hardware Provisioning, and Leave Management Sagas.
- **Presenter Script:** *"To deliver these results safely, we establish a strict operational boundary across four high-volume workflows: routine policy inquiries, cross-policy knowledge synthesis, automated hardware provisioning with approval workflows, and multi-day statutory leave booking with medical certificate tracking. Anything outside this scope—such as harassment complaints, disciplinary matters, or compensation negotiations—is immediately routed to Human HRBPs with full conversation context."*

#### 🎯 Slide 4: Requirements Traceability: Built Strictly to BRD Specs (04:45 - 06:15)
- **Visual Focus:** Clean requirements matrix mapping Functional Requirements (FR-1 to FR-5) against Non-Functional Requirements (NFR-1 to NFR-4) and Section 7 Success Benchmarks.
- **Presenter Script:** *"This architecture is 100% derived from our formal Business Requirements Document (`BRD_MVP1.md`). On the functional axis: dynamic tool calling under enterprise RBAC (FR-1), mandatory provenance attribution tagging every automated action as `AI_HR_AGENT_MVP1` (FR-2), conversational policy section citations like `POL-HR-01#sec-1.1` (FR-3), working days calendar calculations excluding holidays (FR-4), and incident priority anti-inflation (FR-5). On the non-functional axis: strict sub-3.5s latency budgets, Zero-Trust IAP security, 99.9% availability, and in-memory DLP data privacy."*

#### 🎯 Slide 5: Logical Architecture: 6-Tier Enterprise Systems Topology (06:15 - 08:30)
- **Visual Focus:** 6-tier logical architecture cards detailing the specific functional responsibility of each tier.
- **Presenter Script:** *"Our logical architecture maps directly to SDD Block 0 across six decoupled tiers:
  - **Tier 1 (Presentation):** Multi-channel conversational ingress across Slack, Teams, and Web Portals.
  - **Tier 2 (Ingress Security):** Google Cloud IAP edge authentication, corporate IdP OIDC JWKS token validation, and sub-millisecond regex pre-scanning blocking prompt injection in 0.04ms.
  - **Tier 3 (Reasoning Core):** Gemini 3.5 Flash on Cloud Run executing tool plans with 75% cached token economy, wrapped by deterministic Python middleware enforcing calendar math and priority rules.
  - **Tier 4 (Durable State):** Cloud Firestore Native Write-Ahead Logging maintaining ACID state consistency for Two-Phase Sagas, and Cloud Tasks coordinating retries and DLQ isolation.
  - **Tier 5 (Integration Gateway):** Model Context Protocol (MCP) SaaS Adapter communicating over JSON-RPC 2.0 with Secret Manager bearer token injection (`X-MCP-Token`), completely decoupling model prompts from backend SaaS APIs across Workday and ServiceNow.
  - **Tier 6 (Audit & Telemetry):** Tamper-proof audit logging in BigQuery encrypted with Customer-Managed Keys (Cloud KMS CMEK) supporting GDPR/PDPA cryptographic shredding."*

#### 🎯 Slide 6: The OKF Tri-Hybrid Brain (08:30 - 10:15)
- **Visual Focus:** Tri-hybrid mathematical fusion formulation ($RRF\ k=60$), concrete policy grounding matrix (`POL-HR-04`), and kinship decision tree.
- **Presenter Script:** *"Why do standard RAG systems fail in human resources? Because vector similarity alone cannot reliably resolve strict dollar thresholds, statutory holiday schedules, and kinship tiers. We engineered the Open Knowledge Format (OKF) Tri-Hybrid Brain. It fuses dense semantic vectors (`text-embedding-004`), sparse BM25 token matching, and deterministic Rule Graphs using Reciprocal Rank Fusion ($k=60$). For example, under `POL-HR-04`, immediate family bereavement deterministically yields 5 working days, extended family yields 3 days, and pet bereavement is deterministically rejected and routed to annual vacation leave. Policy logic is non-stochastic and absolute."*

#### 🎯 Slide 7: Security & Governance: Google SAIF & Zero Retention (10:15 - 11:45)
- **Visual Focus:** SAIF defense-in-depth architecture, sub-15ms heuristic pre-scan (0.04ms actual), Cloud KMS CMEK encryption, in-memory DLP, and emergency kill-switch.
- **Presenter Script:** *"Security and privacy are engineered into every layer under Google's Secure AI Framework (SAIF). Cloud IAP enforces perimeter authentication, while in-process regex filtering drops prompt injections in 0.04ms. In-memory DLP redacts employee identifiers and medical diagnoses before audit logging. All state is protected by Customer-Managed Encryption Keys via Cloud KMS. Most importantly, under Google Cloud Vertex AI commercial terms, customer prompts are contractually guaranteed never to be retained or used for foundation model training. An emergency kill-switch endpoint halts autonomous execution in under 50 milliseconds."*

#### 🎯 Slide 8: Adoption Roadmap: From Week 3 to 10,000 Users (11:45 - 13:15)
- **Visual Focus:** Phased rollout timeline from Week 3 Champions (100) to Week 4 Feedback Pilot (1,000) to Enterprise Scale (10,000).
- **Presenter Script:** *"Our deployment roadmap minimizes operational risk while accelerating value realization. In Weeks 1–2, we deploy the foundation infrastructure. In Week 3, we onboard 100 HR and IT power users to calibrate policy boundary conditions. In Week 4, we expand to a 1,000-user pilot across engineering and sales, validating our 40% deflection target and gathering live employee feedback. By Month 2, we scale globally across all 10,000 employees, reaching mature 85% deflection and capturing our full $2.04M annual savings run rate."*

#### 🎯 Slide 9: Strategic Summary & Next Steps (13:15 - 15:00)
- **Visual Focus:** Minimalist closing title, pilot authorization scope, contact information, and repository link (`https://github.com/CHOLHOJONG/my-agent`).
- **Presenter Script:** *"In summary: $540,000 in Year 1 net savings, 99% reduction in turnaround time from 72 hours to 3.5 seconds, non-stochastic policy grounding with 99.8% verified accuracy, and 1,250 hours returned every month to our HR team. The codebase and architecture are fully verified. We invite the committee to authorize our Phase 1 pilot today under the $150/month zero-CapEx budget allocation. We are now open for your questions."*

---

## 3. Persona-Specific C-Suite Alignment

| Persona | Primary Mandate | Core Proof & Alignment in 9-Slide Deck |
|---|---|---|
| **Evelyn Vance (CEO)** | Shareholder Value & Risk Governance | $150k/mo labor bleed (Slide 1) &rarr; $540k net Yr 1 savings (Slide 2) with live ROI engine. Zero unscientific claims of "0% hallucination"; 99.8% grounded accuracy. |
| **Marcus Sterling (CPO)** | TCO Dominance & Budget Predictability | Serverless Cloud Run $0 idle cost; Gemini 3.5 Flash context caching (75% discount); 1,000-user pilot capped under $150/mo requiring zero CapEx committee approval. |
| **Dr. Aris Thorne (CDO)** | Grounded Knowledge & Data Value Patterns | OKF Tri-Hybrid Brain (Slide 6) with RRF ($k=60$) fusing Vector, BM25, and Rule Graphs. Deterministic kinship rules (5d immediate vs 3d extended; pet rejection to PTO). |
| **Vikram Malhotra (EA)** | Logical Architecture & MCP Decoupling | 6-tier logical architecture (Slide 5) detailing responsibilities of each tier. Model Context Protocol (MCP) JSON-RPC client adapter decouples model prompts from SaaS APIs. |
| **Helena Zhao (CISO)** | Zero-Trust Identity, SAIF & Data Privacy | Google SAIF (Slide 7): Cloud IAP, OIDC JWKS, 0.04ms regex pre-scan, in-memory DLP, Cloud KMS CMEK crypto-shredding, and contractual zero retention on Vertex AI. |
| **Sarah Jenkins (CHRO)** | Employee Trust & HRBP Capacity | Liberates 1,250 hours/month for HR Business Partners (Slide 2). Mandatory handbook citations (`POL-HR-01#sec-1.1`) and 48-hour MC grace window build employee trust. |
