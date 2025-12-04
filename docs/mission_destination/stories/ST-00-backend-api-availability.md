---
story_id: ST-00
slug: st-00-backend-api-availability
name: Provide Basic Backend API Availability
epic: E00
feature: FT-00-BE
status: in_progress

# MissionSmith Status Fields (used by CI + tools/*.py)
testing_status: pass
halo_adherence: not_run
guardrail_adherence: pass
code_quality_adherence: pass
security_policy_adherence: pass
implementation_presence: partial
last_updated: 2025-12-04
---

## Description

As a developer,  
I want the backend to expose a basic availability endpoint,  
so that I can confirm the service is running and reachable.

This story establishes the foundational API contract for the backend and enables fast automated verification that the service is alive.

## Acceptance Criteria

- **AC1:** Backend can be started using the documented command (e.g. `uvicorn app_backend.main:app`).
- **AC2:** A `/health` endpoint is available.
- **AC3:** Calling `/health` returns HTTP **200**.
- **AC4:** Response JSON contains at least `{ "status": "ok" }`.
- **AC5:** A backend test exercises AC2–AC4.
- **AC6:** Running the story test updates `testing_status:` to `pass` when successful.

## Implementation Notes

- Touchpoint: `app_backend/main.py`
- This endpoint underpins availability checks for the entire platform and is required before any higher-level stories can be executed.




