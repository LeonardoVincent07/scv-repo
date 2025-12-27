---
story_id: ST-28
feature: FT-14
name: "Compute freshness"
description: |
  Freshness score.

acceptance_criteria:
  - Score correct

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
# Compute Freshness

## Statement
As a compliance or operations user, I want data freshness to be computed so that I can assess how up to date client information is.

## Description
Client data may become stale as time passes without updates from source systems.  
The platform must compute freshness indicators for client data based on timestamps, update frequency, or source characteristics.

Freshness indicators support informed decision-making and data quality assessment.

## Acceptance Criteria
- **Given** client data exists  
  **When** freshness computation is performed  
  **Then** freshness indicators are calculated for relevant data

- **Given** underlying data is updated  
  **When** freshness is recomputed  
  **Then** indicators reflect the latest state

- **Given** freshness cannot be determined  
  **When** computation is attempted  
  **Then** this is indicated clearly
