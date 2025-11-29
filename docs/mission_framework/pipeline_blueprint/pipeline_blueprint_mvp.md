
# Pipeline Blueprint — MissionSmith MVP CI/CD Specification

This document defines the mandatory structure, sequencing, governance, and evidence
requirements for the CI/CD pipeline used by Single Client View (SCV) and all MissionSmith-
aligned applications.

It belongs under **MissionFramework**, because it defines system‑wide governance rules for:
- how change flows through the system,
- how evidence is produced,
- how guardrails are enforced,
- how deployment occurs safely.

Recommended location:
`scv-repo/docs/mission_framework/pipeline_blueprint/pipeline_blueprint_mvp.md`

---

## 1. Pipeline Overview

The pipeline consists of six sequential stages:

1. Validate Semantic Artefacts  
2. Generate Tests  
3. Execute Tests  
4. Run Guardrails & Framework Checks  
5. Capture Evidence & Publish MissionLog Snapshot  
6. Deploy (conditional)

A failure in any stage halts all further stages.

---

## 2. Stage 1 — Validate Semantic Artefacts

**Purpose**  
Ensure Epics, Features, Stories, Prompts, MissionFramework artefacts, and MissionHalo
documents are structurally valid and machine-readable.

**Checks**
- YAML front matter correctness  
- story → feature → epic references resolve  
- required adherence fields present  
- no missing or duplicate IDs  
- correct folder structure  
- MissionFramework & MissionHalo documents present and readable  
- prompts exist and are valid  

**Evidence**
- `evidence/semantic_validation.json`  
  - pass/fail per artefact  
  - schema and structure checks  

---

## 3. Stage 2 — Generate Tests (from Test Meta-Prompt)

**Purpose**  
Ensure every Story has a current, valid test suite aligned to acceptance criteria.

**Behaviour**
- Call Test Meta-Prompt for:
  - Stories changed,
  - Stories missing tests,
  - Stories with implementation changes.
- Update tests only in authorised slices:
  `tests/services/<service>/test_service.py`

**Evidence**
- `evidence/test_generation.json`

---

## 4. Stage 3 — Execute Tests

**Purpose**  
Validate Story behaviour.

**Behaviour**
- Run pytest  
- Collect:
  - test results  
  - simple coverage metric  

**Evidence**
- `evidence/test_results.json`  
- `evidence/test_coverage.json`

---

## 5. Stage 4 — Run Guardrails & Framework Checks

**Purpose**  
Enforce MissionFramework systematically.

### 5.1 Technology Guardrails
- no new files/folders outside permitted slices  
- no forbidden imports  
- no cross-service coupling  
- naming conventions  
- no secrets committed  

### 5.2 Policy-as-Code
- logging format  
- PII masking  
- required audit events  

### 5.3 Business Data Lineage
- lineage metadata exists where required  
- schema alignment  

### 5.4 Technology Components Lineage
- dependency graph consistency  

### 5.5 Self-Healing (MVP)
- retry/circuit-breaker config present where appropriate  
- health-check functions present  

### 5.6 Analytics
- telemetry events present  
- analytics schema alignment  

**Evidence**
- `evidence/guardrails.json`  

---

## 6. Stage 5 — Capture Evidence & Publish Snapshot

**Purpose**  
Record the complete compliance and behavioural state at this commit.

**Evidence artefact**
- `evidence/snapshots/<commit_sha>.json`  
Includes:
- semantic validation  
- test results  
- guardrail outcomes  
- adherence statuses  
- version info  

This feeds MissionLog and MissionAtlas.

---

## 7. Stage 6 — Deploy (conditional)

Deployment only occurs if:
- stages 1–5 passed  
- branch is main  
- semantic versioning rules met  

**Behaviour**
- build artefact  
- publish image  
- deploy to environment  
- publish deployment evidence  

**Evidence**
- `evidence/deployment.json`  

---

## 8. Triggering Rules

- PR: run stages 1–4  
- Push to main: run stages 1–6  
- Daily schedule: run 1–5  
- Tag push: full pipeline including deploy  

---

## 9. Versioning Rules (MVP)

- Story implementation change → patch  
- New Story → minor  
- New Feature → minor  
- New Epic → major  
- Breaking schema/API change → major  

---

## 10. Scope

This is the MVP blueprint.  
Future versions may add:
- performance tests  
- chaos engineering  
- deeper analytics  
- dynamic environment creation  
- multi-agent CI  
