---
story_id: ST-08
feature: FT-04
name: "Apply deltas"
description: |
  Apply detected deltas.

acceptance_criteria:
  - Deltas applied

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
# Apply Upstream Deltas

## Statement
As a data operations user, I want detected upstream deltas to be applied so that the platform state remains aligned with source system changes.

## Description
Once upstream deltas have been identified, the platform must apply those changes to its internal representation of client data.  
Applying deltas ensures that new records are added, updated records are amended, and removed records are handled appropriately.

This process keeps the platform’s client data synchronised with upstream systems without requiring full reloads.

## Acceptance Criteria
- **Given** upstream deltas have been detected  
  **When** delta application is executed  
  **Then** new and updated records are applied to the platform state

- **Given** records are marked as removed  
  **When** deltas are applied  
  **Then** the platform state reflects the removal according to defined rules

- **Given** no deltas are detected  
  **When** delta application runs  
  **Then** no changes are applied
