---
story_id: ST-29
feature: FT-14
name: "Compute completeness"
description: |
  Completeness.

acceptance_criteria:
  - Completeness correct

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
# Compute Completeness

## Statement
As a compliance or operations user, I want data completeness to be computed so that I can assess whether client profiles contain sufficient information.

## Description
Client profiles may be partially populated depending on available source data.  
The platform must compute completeness indicators that describe how fully populated a client profile is relative to expected attributes.

Completeness indicators support data quality monitoring and informed operational decision-making.

## Acceptance Criteria
- **Given** a client profile exists  
  **When** completeness is computed  
  **Then** completeness indicators are calculated for the profile

- **Given** underlying client data changes  
  **When** completeness is recomputed  
  **Then** indicators reflect the updated profile state

- **Given** completeness cannot be fully determined  
  **When** computation is attempted  
  **Then** partial completeness is recorded with clear indicators
