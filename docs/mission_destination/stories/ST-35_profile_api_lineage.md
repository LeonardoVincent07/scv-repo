---
story_id: ST-35
feature: FT-17
name: "Profile API lineage"
description: |
  Lineage in API.

acceptance_criteria:
  - Lineage included

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
# Profile API (Lineage)

## Statement
As a compliance or audit user, I want the profile API to expose lineage information so that I can understand how client profile data was derived.

## Description
In addition to basic profile retrieval, the platform must support exposing lineage information through the profile API.  
This allows consumers to retrieve not only the client profile but also the associated lineage describing data origins and transformations.

Exposing lineage through the API supports transparency, auditability, and integration with governance tooling.

## Acceptance Criteria
- **Given** a client profile with recorded lineage exists  
  **When** the profile API is called with lineage enabled  
  **Then** the profile and associated lineage are returned

- **Given** lineage information is requested  
  **When** it is retrieved  
  **Then** it accurately reflects data sources and processing steps

- **Given** lineage is unavailable  
  **When** the API is called  
  **Then** this is indicated clearly in the response
