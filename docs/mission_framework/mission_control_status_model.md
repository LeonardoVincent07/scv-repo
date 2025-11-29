# Mission Control — Status Tracking Model

This document defines how Mission Control tracks and updates the delivery status of **Epics**, **Features**, and **Stories** across the entire MissionSmith lifecycle. All status information is stored in **YAML front matter** within each artefact and is automatically updated through **commit processing**, **guardrail evaluation**, and **CI evidence ingestion**.

---

# 1. Status Model Overview
Each artefact (Epic, Feature, Story) maintains a consistent set of machine-evaluated statuses:

- **overall_status**
- **testing_status**
- **halo_adherence**
- **guardrail_adherence**
- **code_quality_adherence**
- **security_policy_adherence**
- **implementation_presence** (Stories only)

An artefact can only exist in one of three states:
- **Planned**
- **In Progress**
- **Complete**

Statuses are always derived from machine-readable evidence.

---

# 2. Story Status Model (Atomic Unit)
Stories are independent of one another. Story status is determined solely by its own implementation and checks.

## 2.1 Planned
- No commits to the story’s implementation slice
- No tests exist
- No adherence checks have run

## 2.2 In Progress
A Story becomes In Progress when any of the following occur:
- Commits modify the story’s implementation slice
- A test file exists but tests don’t pass
- One or more adherence checks fail
- Required evidence is missing

## 2.3 Complete
A Story is Complete only when:
- Implementation presence is detected
- All tests pass
- Guardrail checks pass
- Halo checks pass
- Code quality checks pass
- Security policy checks pass

---

# 3. Feature Status Model
Feature status is aggregated from child Stories.

## 3.1 Planned
- All Stories in the Feature are Planned

## 3.2 In Progress
- At least one Story is In Progress or Complete
- Not all Stories are Complete

## 3.3 Complete
- All Stories in the Feature are Complete

---

# 4. Epic Status Model
Epic status is aggregated from child Features.

## 4.1 Planned
- All Features are Planned

## 4.2 In Progress
- At least one Feature is In Progress or Complete
- Not all Features are Complete

## 4.3 Complete
- All Features are Complete

---

# 5. Front Matter Structure

## 5.1 Story Front Matter
```yaml
story_id: ST-123
feature: FT-45

overall_status: Planned | In Progress | Complete

testing_status: pass | fail | not_run
halo_adherence: pass | fail
guardrail_adherence: pass | fail
code_quality_adherence: pass | fail
security_policy_adherence: pass | fail
implementation_presence: true | false

last_updated: 2025-01-01T12:00:00Z
```

## 5.2 Feature Front Matter
```yaml
feature_id: FT-45
epic: EP-7

overall_status: Planned | In Progress | Complete

testing_status: aggregated
halo_adherence: aggregated
guardrail_adherence: aggregated
code_quality_adherence: aggregated
security_policy_adherence: aggregated

story_statuses:
  ST-123: Complete
  ST-124: In Progress
  ST-125: Planned

last_updated: 2025-01-01T12:00:00Z
```

## 5.3 Epic Front Matter
```yaml
epic_id: EP-7

overall_status: Planned | In Progress | Complete

testing_status: aggregated
halo_adherence: aggregated
guardrail_adherence: aggregated
code_quality_adherence: aggregated
security_policy_adherence: aggregated

feature_statuses:
  FT-45: Complete
  FT-46: In Progress
  FT-47: Planned

last_updated: 2025-01-01T12:00:00Z
```

---

# 6. Status Computation Rules
1. Front matter updates occur when:
   - Story implementation slices change
   - Tests run and generate evidence
   - Guardrail checks execute
   - CI pipelines update MissionLog

2. Statuses propagate bottom-up:
   - Story → Feature → Epic

3. No manual modification of status fields.
4. MissionLog reflects live state directly from front matter.

---

# 7. MissionLog Reporting
MissionLog provides:
- Epic / Feature / Story roll-ups
- Per-status dashboards (testing, guardrails, halo, quality, security)
- Evidence lineage
- Completion graphs
- Compliance summaries

MissionLog stores no separate state; it visualises repo truth.

---

# 8. Principles
- Everything lives in the repo
- Status is always derived, never declared
- Stories are atomic
- Features & Epics are compositional
- Front matter is the single source of truth
- MissionLog is read-only
- Automated consistency across levels

