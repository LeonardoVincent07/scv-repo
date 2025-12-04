# Mission Control Status Snapshot

## Epics

| Epic | Name | Overall | Testing | Guardrails | Code Quality | Security |
|------|------|---------|---------|-----------|--------------|----------|
| E00 | Application Bootstrapping | Planned | Planned | Planned | Planned | Planned |
| E00-UI | User Interface Bootstrapping | Planned | Planned | Planned | Planned | Planned |
| EP-01 | Client Ingestion & Normalisation | Planned | In Progress | In Progress | In Progress | In Progress |
| EP-02 | Client Matching & Golden Record | Planned | Planned | In Progress | In Progress | In Progress |
| EP-03 | Client Search | Planned | Planned | In Progress | In Progress | In Progress |
| EP-04 | Client Profile Assembly | Planned | In Progress | In Progress | In Progress | In Progress |
| EP-05 | Data Quality & Lineage | Planned | In Progress | In Progress | In Progress | In Progress |
| EP-06 | Integration & API Exposure | Planned | Planned | In Progress | In Progress | In Progress |


## Features

| Feature | Epic | Name | Overall | Testing | Guardrails | Code Quality | Security | Stories |
|---------|------|------|---------|---------|-----------|--------------|----------|---------|
| FT-00-BE | E00 | Backend Fundamentals | Planned | Planned | Planned | Planned | Planned | ST-00 |
| FT-00-UI | E00-UI | Frontend Fundamentals | Planned | Planned | Planned | Planned | Planned | ST-00-FRONTEND-UI-SHELL |
| FT-01 | EP-01 | Source System Configuration | Planned | Planned | In Progress | In Progress | In Progress | ST-01, ST-02 |
| FT-02 | EP-01 | Schema Mapping to Canonical Model | Planned | Complete | Complete | Complete | Complete | ST-03, ST-04 |
| FT-03 | EP-01 | Initial Bulk Ingestion | Planned | Planned | In Progress | In Progress | In Progress | ST-05, ST-06 |
| FT-04 | EP-01 | Incremental Ingestion & Change Detection | Planned | Planned | In Progress | In Progress | In Progress | ST-07, ST-08 |
| FT-05 | EP-02 | Exact Match Rules | Planned | Planned | In Progress | In Progress | In Progress | ST-09, ST-10 |
| FT-06 | EP-02 | Fuzzy & Probabilistic Matching | Planned | Planned | In Progress | In Progress | In Progress | ST-11, ST-12 |
| FT-07 | EP-02 | Golden Record Construction | Planned | Planned | In Progress | In Progress | In Progress | ST-13, ST-14, ST-15 |
| FT-08 | EP-03 | Search Index & Normalisation | Planned | Planned | In Progress | In Progress | In Progress | ST-16, ST-17 |
| FT-09 | EP-03 | Fuzzy Search & Ranking | Planned | Planned | In Progress | In Progress | In Progress | ST-18, ST-19 |
| FT-10 | EP-04 | Assemble Canonical Profile | Planned | In Progress | In Progress | In Progress | In Progress | ST-20, ST-21 |
| FT-11 | EP-04 | Lineage Exposure | Planned | Planned | In Progress | In Progress | In Progress | ST-22, ST-23 |
| FT-12 | EP-04 | Conflict Presentation | Planned | Planned | In Progress | In Progress | In Progress | ST-24, ST-25 |
| FT-13 | EP-05 | Lineage Tracking | Planned | Planned | In Progress | In Progress | In Progress | ST-26, ST-27 |
| FT-14 | EP-05 | Data Quality Scoring | Planned | Planned | In Progress | In Progress | In Progress | ST-28, ST-29 |
| FT-15 | EP-05 | Auditability & Evidence | Planned | In Progress | In Progress | In Progress | In Progress | ST-30, ST-31 |
| FT-16 | EP-06 | Search API | Planned | Planned | In Progress | In Progress | In Progress | ST-32, ST-33 |
| FT-17 | EP-06 | Client Profile API | Planned | Planned | In Progress | In Progress | In Progress | ST-34, ST-35 |


## Stories

| Story | Feature | Name | Overall | Testing | Guardrails | Code Quality | Security |
|-------|---------|------|---------|---------|-----------|--------------|----------|
| ST-00 | FT-00-BE | Provide Basic Backend API Availability |  | pass | pass | pass | pass |
| ST-00-FRONTEND-UI-SHELL | FT-00-UI | Provide Frontend UI Shell Availability |  | pass | not_run | pass | pass |
| ST-01 | FT-01 | Register CRM source | Planned | not_run | fail | fail | fail |
| ST-02 | FT-01 | Register KYC source | Planned | not_run | fail | fail | fail |
| ST-03 | FT-02 | Map identity fields | Planned | pass | pass | pass | pass |
| ST-04 | FT-02 | Map identifiers | Planned | pass | pass | pass | pass |
| ST-05 | FT-03 | Bulk load CRM | Planned | not_run | fail | fail | fail |
| ST-06 | FT-03 | Bulk load KYC | Planned | not_run | fail | fail | fail |
| ST-07 | FT-04 | Detect upstream deltas | Planned | not_run | fail | fail | fail |
| ST-08 | FT-04 | Apply deltas | Planned | not_run | fail | fail | fail |
| ST-09 | FT-05 | Match by tax ID | Planned | not_run | fail | fail | fail |
| ST-10 | FT-05 | Match by registration number | Planned | not_run | fail | fail | fail |
| ST-11 | FT-06 | Fuzzy name match | Planned | not_run | fail | fail | fail |
| ST-12 | FT-06 | Attribute confidence | Planned | not_run | fail | fail | fail |
| ST-13 | FT-07 | Merge identity | Planned | not_run | fail | fail | fail |
| ST-14 | FT-07 | Merge addresses | Planned | not_run | fail | fail | fail |
| ST-15 | FT-07 | Record lineage | Planned | not_run | fail | fail | fail |
| ST-16 | FT-08 | Build index | Planned | not_run | fail | fail | fail |
| ST-17 | FT-08 | Normalise search fields | Planned | not_run | fail | fail | fail |
| ST-18 | FT-09 | Fuzzy search queries | Planned | not_run | fail | fail | fail |
| ST-19 | FT-09 | Search ranking | Planned | not_run | fail | fail | fail |
| ST-20 | FT-10 | Assemble base profile | Planned | pass | pass | pass | pass |
| ST-21 | FT-10 | Assemble metadata | Planned | not_run | fail | fail | fail |
| ST-22 | FT-11 | Expose lineage | Planned | not_run | fail | fail | fail |
| ST-23 | FT-11 | Drill-down lineage | Planned | not_run | fail | fail | fail |
| ST-24 | FT-12 | Flag conflicts | Planned | not_run | fail | fail | fail |
| ST-25 | FT-12 | Show merge logic | Planned | not_run | fail | fail | fail |
| ST-26 | FT-13 | Store lineage history | Planned | not_run | fail | fail | fail |
| ST-27 | FT-13 | Timestamp lineage | Planned | not_run | fail | fail | fail |
| ST-28 | FT-14 | Compute freshness | Planned | not_run | fail | fail | fail |
| ST-29 | FT-14 | Compute completeness | Planned | not_run | fail | fail | fail |
| ST-30 | FT-15 | Audit ingestion | Planned | pass | fail | pass | pass |
| ST-31 | FT-15 | Audit merge | Planned | not_run | fail | fail | fail |
| ST-32 | FT-16 | Search API basic | Planned | not_run | fail | fail | fail |
| ST-33 | FT-16 | Search API ranking | Planned | not_run | fail | fail | fail |
| ST-34 | FT-17 | Profile API basic | Planned | not_run | fail | fail | fail |
| ST-35 | FT-17 | Profile API lineage | Planned | not_run | fail | fail | fail |
