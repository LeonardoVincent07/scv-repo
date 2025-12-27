---
story_id: ST-34
feature: FT-17
name: "Profile API basic"
description: |
  Profile endpoint.

acceptance_criteria:
  - Profile returned

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
# Profile API (Basic)

## Statement
As an application or operations user, I want a basic profile API so that consolidated client profiles can be retrieved programmatically.

## Description
The platform must expose a basic profile API that allows authorised consumers to retrieve assembled client profiles.  
The API provides programmatic access to the platform’s consolidated view of a client and supports integration with downstream systems and user interfaces.

The basic profile API focuses on core profile retrieval without advanced metadata or lineage detail.

## Acceptance Criteria
- **Given** a client profile exists  
  **When** the basic profile API is called with a valid identifier  
  **Then** the client profile is returned successfully

- **Given** a requested profile does not exist  
  **When** the API is called  
  **Then** a clear “not found” response is returned

- **Given** invalid request parameters are provided  
  **When** the API is called  
  **Then** a clear error response is returned
