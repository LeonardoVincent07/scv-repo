---
story_id: ST-31
feature: FT-15
name: "Audit merge"
description: |
  Audit merge.

acceptance_criteria:
  - Audit recorded

overall_status: Planned

testing_status: not_run
halo_adherence: not_run
guardrail_adherence: not_run
code_quality_adherence: not_run
security_policy_adherence: not_run

policy_adherence: not_run
technology_lineage_adherence: not_run
business_data_lineage_adherence: not_run
self_healing_adherence: not_run
analytics_adherence: not_run
last_updated: <auto>
---
# Audit Merge

## Statement
As a compliance or audit user, I want merge activity to be audited so that I can understand how client records were consolidated.

## Description
When client records are merged, the platform must record audit information describing the merge activity.  
Audit records should capture which records were merged, when the merge occurred, and the outcome.

Auditing merge activity supports transparency, investigation, and regulatory compliance.

## Acceptance Criteria
- **Given** client records are merged  
  **When** the merge completes  
  **Then** an audit record is created for the merge activity

- **Given** merge audit records exist  
  **When** they are requested  
  **Then** they can be retrieved and reviewed

- **Given** merge auditing fails  
  **When** merging proceeds  
  **Then** the failure is reported clearly
