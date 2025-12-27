---
story_id: ST-10
feature: FT-05
name: "Match by registration number"
description: |
  Exact match.

acceptance_criteria:
  - Matches correct

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
# Match Clients by Registration Number

## Statement
As a compliance operations user, I want clients to be matched by registration number so that records referring to the same legal entity can be identified reliably.

## Description
Client records originating from different systems may refer to the same legal entity using a common registration number.  
The platform must support matching client records based on registration number as a strong identifier.

Matching by registration number complements other matching strategies and improves the accuracy of client consolidation.

## Acceptance Criteria
- **Given** multiple client records exist  
  **When** matching by registration number is performed  
  **Then** records with the same registration number are identified as potential matches

- **Given** registration number matches are identified  
  **When** downstream processing occurs  
  **Then** those records are treated as referring to the same entity

- **Given** a registration number is missing or invalid  
  **When** matching is attempted  
  **Then** the limitation is reported clearly
