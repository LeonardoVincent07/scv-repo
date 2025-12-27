---
story_id: ST-25
feature: FT-12
name: "Show merge logic"
description: |
  Show logic.

acceptance_criteria:
  - Logic displayed

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
# Show Merge Logic

## Statement
As a compliance or audit user, I want to understand how merge decisions were made so that client data consolidation is transparent.

## Description
When client data is merged, the platform applies rules and logic to determine which values are retained.  
The platform must expose the merge logic applied to client attributes so that users can understand why specific values were chosen.

Showing merge logic supports auditability, trust, and investigation of client profile outcomes.

## Acceptance Criteria
- **Given** client attributes have been merged  
  **When** merge logic is requested  
  **Then** the applied rules and outcomes are displayed clearly

- **Given** merge logic is displayed  
  **When** it is reviewed  
  **Then** it explains why specific values were retained

- **Given** merge logic cannot be determined  
  **When** it is requested  
  **Then** this is indicated clearly
