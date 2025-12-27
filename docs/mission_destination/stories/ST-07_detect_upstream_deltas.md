---
story_id: ST-07
feature: FT-04
name: "Detect upstream deltas"
description: |
  Detect deltas.

acceptance_criteria:
  - Changes detected

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
# Detect Upstream Deltas

## Statement
As a data operations user, I want the platform to detect upstream data changes so that only new or modified client records are processed incrementally.

## Description
Upstream source systems may deliver repeated data extracts containing a mixture of unchanged, new, updated, or removed records.  
The platform must be able to compare incoming data against previously ingested data to detect meaningful deltas.

Detecting upstream deltas enables efficient incremental processing and prevents unnecessary reprocessing of unchanged client records.

## Acceptance Criteria
- **Given** a previous ingestion has occurred  
  **When** new data is received from the same source system  
  **Then** the platform identifies new, changed, and unchanged records

- **Given** upstream records have not changed  
  **When** delta detection runs  
  **Then** those records are marked as unchanged

- **Given** records are new or updated  
  **When** delta detection completes  
  **Then** they are flagged for downstream processing

