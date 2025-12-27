---
story_id: ST-22
feature: FT-11
name: "Expose lineage"
description: |
  Lineage display.

acceptance_criteria:
  - Lineage visible

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
# Expose Lineage

## Statement
As a compliance or audit user, I want lineage information to be exposed so that downstream systems and users can understand how client data was derived.

## Description
The platform must make data lineage information available through a controlled interface.  
Exposed lineage describes the origin of data, the transformations applied, and the processes involved in producing client profiles.

Exposing lineage enables transparency, auditability, and integration with downstream tools.

## Acceptance Criteria
- **Given** lineage information exists  
  **When** lineage is requested  
  **Then** the information is returned successfully

- **Given** lineage is exposed  
  **When** it is consumed  
  **Then** it accurately reflects source systems and transformations

- **Given** lineage is unavailable for a request  
  **When** exposure is attempted  
  **Then** this is indicated clearly
