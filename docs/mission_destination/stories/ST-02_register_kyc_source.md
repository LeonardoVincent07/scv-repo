---
story_id: ST-02
feature: FT-01
name: "Register KYC source"
description: |
  Register KYC system.

acceptance_criteria:
  - Connection ok
  - Schema ok

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
# Register KYC Source System

## Statement
As a compliance operations user, I want to register a KYC source system so that client due-diligence data can be ingested and governed with clear provenance.

## Description
The platform must support the registration of KYC source systems as approved providers of compliance and due-diligence data.  
Registering a KYC source system ensures that KYC data entering the platform can be traced back to its originating system and treated according to governance and compliance requirements.

Once registered, the KYC source system can be referenced by ingestion, enrichment, and profile assembly processes.

## Acceptance Criteria
- **Given** a KYC source system has not previously been registered  
  **When** a compliance operations user registers the KYC source system  
  **Then** the system is stored as a recognised and active KYC data source

- **Given** a KYC source system is registered  
  **When** KYC data is ingested  
  **Then** the data is associated with the registered source system

- **Given** invalid or incomplete registration details are provided  
  **When** the registration is attempted  
  **Then** the registration is rejected with a clear error message
