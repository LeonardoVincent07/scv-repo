---
story_id: ST-03
feature: FT-02
name: "Map identity fields"
description: |
  Map core identity fields.

acceptance_criteria:
  - Fields mapped
  - Types correct

overall_status: In Progress

testing_status: not_run
halo_adherence: not_run
guardrail_adherence: fail
code_quality_adherence: not_run
security_policy_adherence: not_run

policy_adherence: not_run
technology_lineage_adherence: not_run
business_data_lineage_adherence: not_run
self_healing_adherence: not_run
analytics_adherence: not_run
last_updated: 2025-12-21T16:19:34Z
---
# Map Identity Fields

## Statement
As a data operations user, I want to map identity fields so that equivalent client attributes from different source systems can be normalised and compared consistently.

## Description
Client identity data may be provided by multiple source systems using different field names and structures.  
The platform must support mapping source-specific identity fields to a canonical representation so that identity information can be processed consistently across the platform.

Mapped identity fields form the basis for downstream matching, profile assembly, and lineage reporting.

## Acceptance Criteria
- **Given** identity fields exist in a source system  
  **When** identity field mappings are defined  
  **Then** the fields are mapped to the platform’s canonical identity model

- **Given** identity mappings are defined  
  **When** client data is ingested  
  **Then** identity values are normalised according to the mappings

- **Given** a required identity field is unmapped  
  **When** identity processing is attempted  
  **Then** the issue is reported clearly
