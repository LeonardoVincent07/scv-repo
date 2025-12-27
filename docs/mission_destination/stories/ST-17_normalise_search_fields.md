---
story_id: ST-17
feature: FT-08
name: "Normalise search fields"
description: |
  Normalise fields.

acceptance_criteria:
  - Fields normalised

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
# Normalise Search Fields

## Statement
As an operations user, I want search fields to be normalised so that client data can be searched consistently regardless of source formatting.

## Description
Client data may be represented differently across source systems, including variations in casing, formatting, and structure.  
The platform must normalise search-relevant fields into a consistent representation suitable for indexing and querying.

Normalised search fields improve search accuracy and user experience.

## Acceptance Criteria
- **Given** client data contains searchable attributes  
  **When** normalisation is performed  
  **Then** search fields are transformed into a consistent format

- **Given** normalised search fields  
  **When** indexing occurs  
  **Then** the normalised values are used

- **Given** a field cannot be normalised  
  **When** processing occurs  
  **Then** the limitation is reported clearly
