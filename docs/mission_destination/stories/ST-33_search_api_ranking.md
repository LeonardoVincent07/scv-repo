---
story_id: ST-33
feature: FT-16
name: "Search API ranking"
description: |
  Ranking via API.

acceptance_criteria:
  - Ranked results

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
# Search API (Ranking)

## Statement
As an application or operations user, I want the search API to return ranked results so that the most relevant client profiles are prioritised.

## Description
Building on the basic search API, the platform must support ranked search results.  
Ranking logic orders results based on relevance criteria such as match strength, confidence, or completeness.

Ranked search improves usability and effectiveness for both users and integrated systems.

## Acceptance Criteria
- **Given** multiple search results are returned  
  **When** ranked search is performed  
  **Then** results are ordered by relevance

- **Given** ranking criteria are applied  
  **When** the search API is called  
  **Then** results reflect the ranking logic

- **Given** ranking cannot be applied  
  **When** the API is called  
  **Then** results are returned without ranking and the limitation is reported
