---
epic_id: E00
slug: e00_application_bootstrapping
name: "Application Bootstrapping"
description: |
  Establish the initial backend service and runtime foundations required for the
  Single Client View application to start, respond to basic requests, and be
  governed by MissionFramework guardrails.

features:
  - FT-00

overall_status: In Progress

testing_status: aggregated
halo_adherence: aggregated
guardrail_adherence: aggregated
code_quality_adherence: aggregated
security_policy_adherence: aggregated

last_updated: <auto>
---

## Context

This epic delivers the minimal backend scaffolding needed for developers to
build, run, and verify the Single Client View application.

## Objectives

- Backend starts reliably in a developer environment.
- At least one health/status endpoint is available.
- Code adheres to MissionFramework guardrails.
- Story-level test status is automatically updated.

## Acceptance

- All features under this epic have status `active` or `done`.
- All related stories have `testing_status: pass`.

