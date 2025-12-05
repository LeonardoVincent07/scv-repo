# Mission Control Status Snapshot

## Epics

| Epic | Name | Overall |
|------|------|---------|
| E00 | Application Bootstrapping | Complete |
| E00-UI | User Interface Bootstrapping | In Progress |
| EP-01 | Client Ingestion & Normalisation | In Progress |
| EP-02 | Client Matching & Golden Record | In Progress |
| EP-03 | Client Search | In Progress |
| EP-04 | Client Profile Assembly | In Progress |
| EP-05 | Data Quality & Lineage | In Progress |
| EP-06 | Integration & API Exposure | In Progress |


## Features

| Feature | Epic | Name | Overall | Stories |
|---------|------|------|---------|---------|
| FT-00-BE | E00 | Backend Fundamentals | Complete | ST-00 |
| FT-00-UI | E00-UI | Frontend Fundamentals | In Progress | ST-00-FRONTEND-UI-SHELL |
| FT-01 | EP-01 | Source System Configuration | In Progress | ST-01, ST-02 |
| FT-02 | EP-01 | Schema Mapping to Canonical Model | In Progress | ST-03, ST-04 |
| FT-03 | EP-01 | Initial Bulk Ingestion | In Progress | ST-05, ST-06 |
| FT-04 | EP-01 | Incremental Ingestion & Change Detection | In Progress | ST-07, ST-08 |
| FT-05 | EP-02 | Exact Match Rules | In Progress | ST-09, ST-10 |
| FT-06 | EP-02 | Fuzzy & Probabilistic Matching | In Progress | ST-11, ST-12 |
| FT-07 | EP-02 | Golden Record Construction | In Progress | ST-13, ST-14, ST-15 |
| FT-08 | EP-03 | Search Index & Normalisation | In Progress | ST-16, ST-17 |
| FT-09 | EP-03 | Fuzzy Search & Ranking | In Progress | ST-18, ST-19 |
| FT-10 | EP-04 | Assemble Canonical Profile | In Progress | ST-20, ST-21 |
| FT-11 | EP-04 | Lineage Exposure | In Progress | ST-22, ST-23 |
| FT-12 | EP-04 | Conflict Presentation | In Progress | ST-24, ST-25 |
| FT-13 | EP-05 | Lineage Tracking | In Progress | ST-26, ST-27 |
| FT-14 | EP-05 | Data Quality Scoring | In Progress | ST-28, ST-29 |
| FT-15 | EP-05 | Auditability & Evidence | In Progress | ST-30, ST-31 |
| FT-16 | EP-06 | Search API | In Progress | ST-32, ST-33 |
| FT-17 | EP-06 | Client Profile API | In Progress | ST-34, ST-35 |


## Stories

| Story | Feature | Name | Overall |
|-------|---------|------|---------|
| ST-00 | FT-00-BE | Provide Basic Backend API Availability | Complete |
| ST-00-FRONTEND-UI-SHELL | FT-00-UI | Provide Frontend UI Shell Availability | In Progress |
| ST-01 | FT-01 | Register CRM source | In Progress |
| ST-02 | FT-01 | Register KYC source | In Progress |
| ST-03 | FT-02 | Map identity fields | In Progress |
| ST-04 | FT-02 | Map identifiers | In Progress |
| ST-05 | FT-03 | Bulk load CRM | In Progress |
| ST-06 | FT-03 | Bulk load KYC | In Progress |
| ST-07 | FT-04 | Detect upstream deltas | In Progress |
| ST-08 | FT-04 | Apply deltas | In Progress |
| ST-09 | FT-05 | Match by tax ID | In Progress |
| ST-10 | FT-05 | Match by registration number | In Progress |
| ST-11 | FT-06 | Fuzzy name match | In Progress |
| ST-12 | FT-06 | Attribute confidence | In Progress |
| ST-13 | FT-07 | Merge identity | In Progress |
| ST-14 | FT-07 | Merge addresses | In Progress |
| ST-15 | FT-07 | Record lineage | In Progress |
| ST-16 | FT-08 | Build index | In Progress |
| ST-17 | FT-08 | Normalise search fields | In Progress |
| ST-18 | FT-09 | Fuzzy search queries | In Progress |
| ST-19 | FT-09 | Search ranking | In Progress |
| ST-20 | FT-10 | Assemble base profile | In Progress |
| ST-21 | FT-10 | Assemble metadata | In Progress |
| ST-22 | FT-11 | Expose lineage | In Progress |
| ST-23 | FT-11 | Drill-down lineage | In Progress |
| ST-24 | FT-12 | Flag conflicts | In Progress |
| ST-25 | FT-12 | Show merge logic | In Progress |
| ST-26 | FT-13 | Store lineage history | In Progress |
| ST-27 | FT-13 | Timestamp lineage | In Progress |
| ST-28 | FT-14 | Compute freshness | In Progress |
| ST-29 | FT-14 | Compute completeness | In Progress |
| ST-30 | FT-15 | Audit ingestion | In Progress |
| ST-31 | FT-15 | Audit merge | In Progress |
| ST-32 | FT-16 | Search API basic | In Progress |
| ST-33 | FT-16 | Search API ranking | In Progress |
| ST-34 | FT-17 | Profile API basic | In Progress |
| ST-35 | FT-17 | Profile API lineage | In Progress |
