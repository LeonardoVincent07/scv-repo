---
story_id: ST-00-FRONTEND-UI-SHELL
slug: st-00-frontend-ui-shell
name: Provide Frontend UI Shell Availability
epic: E00-UI
feature: FT-00-UI
status: in_progress

# MissionSmith Status Fields (used by CI + tools/*.py)
testing_status: pass
halo_adherence: not_run
guardrail_adherence: not_run
code_quality_adherence: pass
security_policy_adherence: pass
implementation_presence: partial
overall_status: In Progress
last_updated: 2025-12-04
---

## Description

As a developer,  
I want the frontend UI shell to be built and served by the backend,  
so that I can confirm the Single Client View application is accessible as a SPA.

This story verifies that the built frontend exists and the backend correctly serves
the index.html shell at the root path.

## Acceptance Criteria

- **AC1:** `npm run build` produces a frontend `dist/` folder.
- **AC2:** Backend is configured to serve the frontend build output.
- **AC3:** `GET /` returns HTTP **200**.
- **AC4:** HTML contains `<div id="root">`.
- **AC5:** HTML contains the expected page `<title>` from the built frontend.
- **AC6:** A backend test verifies AC1–AC5.
- **AC7:** Running the ST-00-FRONTEND-UI-SHELL tests sets `testing_status: pass`.

## Implementation Notes

- Frontend: `app_frontend/`
- Backend serving logic: `app_backend/main.py`
- Test: `tests/api/http/test_st_00_frontend_ui_shell.py`




