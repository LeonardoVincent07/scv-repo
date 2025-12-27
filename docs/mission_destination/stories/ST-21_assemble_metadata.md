---
story_id: ST-21
feature: FT-10
name: "Assemble metadata"
description: |
  Assemble metadata.

acceptance_criteria:
  - Metadata added

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
# Assemble Profile Metadata

## Statement
As a compliance or operations user, I want profile metadata to be assembled so that I can assess the quality and state of a client profile.

## Description
In addition to core client data, the platform must derive and assemble metadata about each client profile.  
Profile metadata may include indicators such as completeness, freshness, confidence, and references to lineage or evidence.

This metadata supports informed decision-making and operational oversight of client profiles.

## Acceptance Criteria
- **Given** a client profile exists  
  **When** metadata assembly is performed  
  **Then** profile metadata is calculated and associated with the profile

- **Given** underlying client data changes  
  **When** metadata is reassembled  
  **Then** metadata reflects the updated profile state

- **Given** metadata cannot be fully derived  
  **When** assembly is attempted  
  **Then** partial metadata is recorded with clear indicators

