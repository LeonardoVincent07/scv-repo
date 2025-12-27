---
story_id: ST-15
feature: FT-07
name: "Record lineage"
description: |
  Lineage for merges.

acceptance_criteria:
  - Lineage stored

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
# Record Lineage

## Statement
As a compliance or audit user, I want lineage to be recorded so that the origin and transformation of client data can be traced over time.

## Description
As client data is ingested, matched, merged, and assembled, the platform must record lineage information describing how the data was produced.  
Recorded lineage provides the foundation for auditability, transparency, and trust in client profiles.

Lineage records must be associated with the relevant data and processing events.

## Acceptance Criteria
- **Given** client data is processed  
  **When** processing occurs  
  **Then** lineage information is recorded for the relevant events

- **Given** lineage has been recorded  
  **When** it is queried  
  **Then** it accurately reflects data origins and transformations

- **Given** lineage recording fails  
  **When** processing continues  
  **Then** the failure is reported clearly
