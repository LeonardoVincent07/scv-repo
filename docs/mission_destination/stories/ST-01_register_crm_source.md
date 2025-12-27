---
story_id: ST-01
feature: FT-01
name: "Register CRM source"
description: |
  Register CRM system as ingestible source.

acceptance_criteria:
  - Connection succeeds
  - Schema retrieved

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
# Register CRM Source System

## Statement
As a data operations user, I want to register a CRM source system so that client data ingested from that system can be correctly identified, governed, and traced throughout the platform.

## Description
The platform must allow a CRM source system to be registered as an approved upstream data provider.  
Registering a CRM source system establishes it as a recognised origin for client data and enables downstream ingestion, mapping, matching, and lineage tracking.

The registration process captures the minimum information required to uniquely identify the CRM system and treat it as a governed source within the platform. Once registered, the CRM source system can be referenced consistently by ingestion and processing workflows.

## Acceptance Criteria
- **Given** a CRM source system has not previously been registered  
  **When** a data operations user registers the CRM source system  
  **Then** the system is stored as a recognised and active source

- **Given** a CRM source system is registered  
  **When** downstream processes reference the source  
  **Then** the system is identifiable as the origin of ingested client data

- **Given** an attempt is made to register a CRM source system with missing or invalid identifying information  
  **When** the registration is submitted  
  **Then** the registration is rejected with a clear validation error
