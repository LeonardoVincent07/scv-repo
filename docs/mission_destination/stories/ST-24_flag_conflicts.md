---
story_id: ST-24
feature: FT-12
name: "Flag conflicts"
description: |
  Conflict flags.

acceptance_criteria:
  - Flags correct

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
# Flag Conflicts

## Statement
As a compliance or operations user, I want data conflicts to be flagged so that inconsistencies in client information can be identified and addressed.

## Description
When client data from multiple sources is merged or assembled, conflicts may arise between attributes such as identifiers, names, or addresses.  
The platform must detect and flag these conflicts so that they are visible for review and resolution.

Flagging conflicts supports data quality management and prevents silent inconsistencies in client profiles.

## Acceptance Criteria
- **Given** conflicting client attributes are detected  
  **When** profile processing occurs  
  **Then** the conflicts are flagged clearly

- **Given** flagged conflicts exist  
  **When** a client profile is reviewed  
  **Then** the conflicts are visible to the user

- **Given** no conflicts are present  
  **When** processing occurs  
  **Then** no conflict flags are created
