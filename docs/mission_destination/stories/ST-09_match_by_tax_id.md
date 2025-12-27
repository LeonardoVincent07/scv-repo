---
story_id: ST-09
feature: FT-05
name: "Match by tax ID"
description: |
  Exact match by tax ID.

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
# Match Clients by Tax Identifier

## Statement
As a compliance operations user, I want clients to be matched by tax identifier so that duplicate or related client records can be identified accurately.

## Description
Clients may appear in multiple source systems with different representations.  
The platform must support matching client records using tax identifiers as a strong matching attribute.

Successful matching enables consolidation of records that refer to the same real-world entity and reduces duplication in client profiles.

## Acceptance Criteria
- **Given** multiple client records exist  
  **When** matching by tax identifier is performed  
  **Then** records with the same tax identifier are identified as potential matches

- **Given** a tax identifier match is identified  
  **When** client profiles are assembled  
  **Then** matched records are treated as referring to the same client

- **Given** a tax identifier is missing or invalid  
  **When** matching is attempted  
  **Then** the limitation is reported clearly
