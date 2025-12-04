# Mission Control Status Snapshot

## Epics

| Epic | Name | Overall |
|------|------|---------|
| E00 | Application Bootstrapping | Complete |
| E00-UI | User Interface Bootstrapping | Complete |
| EP-01 | Client Ingestion & Normalisation | In Progress |
| EP-02 | Client Matching & Golden Record | Planned |
| EP-03 | Client Search | Planned |
| EP-04 | Client Profile Assembly | In Progress |
| EP-05 | Data Quality & Lineage | In Progress |
| EP-06 | Integration & API Exposure | Planned |


## Features

| Feature | Epic | Name | Overall | Stories |
|---------|------|------|---------|---------|
| FT-00-BE | E00 | Backend Fundamentals | Complete | ST-00 |
| FT-00-UI | E00-UI | Frontend Fundamentals | Complete | ST-00-FRONTEND-UI-SHELL |
| FT-01 | EP-01 | Source System Configuration | Planned | ST-01, ST-02 |
| FT-02 | EP-01 | Schema Mapping to Canonical Model | In Progress | ST-03, ST-04 |
| FT-03 | EP-01 | Initial Bulk Ingestion | Planned | ST-05, ST-06 |
| FT-04 | EP-01 | Incremental Ingestion & Change Detection | Planned | ST-07, ST-08 |
| FT-05 | EP-02 | Exact Match Rules | Planned | ST-09, ST-10 |
| FT-06 | EP-02 | Fuzzy & Probabilistic Matching | Planned | ST-11, ST-12 |
| FT-07 | EP-02 | Golden Record Construction | Planned | ST-13, ST-14, ST-15 |
| FT-08 | EP-03 | Search Index & Normalisation | Planned | ST-16, ST-17 |
| FT-09 | EP-03 | Fuzzy Search & Ranking | Planned | ST-18, ST-19 |
| FT-10 | EP-04 | Assemble Canonical Profile | In Progress | ST-20, ST-21 |
| FT-11 | EP-04 | Lineage Exposure | Planned | ST-22, ST-23 |
| FT-12 | EP-04 | Conflict Presentation | Planned | ST-24, ST-25 |
| FT-13 | EP-05 | Lineage Tracking | Planned | ST-26, ST-27 |
| FT-14 | EP-05 | Data Quality Scoring | Planned | ST-28, ST-29 |
| FT-15 | EP-05 | Auditability & Evidence | In Progress | ST-30, ST-31 |
| FT-16 | EP-06 | Search API | Planned | ST-32, ST-33 |
| FT-17 | EP-06 | Client Profile API | Planned | ST-34, ST-35 |


## Stories

| Story | Feature | Name | Overall |
|-------|---------|------|---------|
| ST-00 | FT-00-BE | Provide Basic Backend API Availability | Complete |
| ST-00-FRONTEND-UI-SHELL | FT-00-UI | Provide Frontend UI Shell Availability | Complete |
| ST-01 | FT-01 | Register CRM source | Planned |
| ST-02 | FT-01 | Register KYC source | Planned |
| ST-03 | FT-02 | Map identity fields | In Progress |
| ST-04 | FT-02 | Map identifiers | In Progress |
| ST-05 | FT-03 | Bulk load CRM | Planned |
| ST-06 | FT-03 | Bulk load KYC | Planned |
| ST-07 | FT-04 | Detect upstream deltas | Planned |
| ST-08 | FT-04 | Apply deltas | Planned |
| ST-09 | FT-05 | Match by tax ID | Planned |
| ST-10 | FT-05 | Match by registration number | Planned |
| ST-11 | FT-06 | Fuzzy name match | Planned |
| ST-12 | FT-06 | Attribute confidence | Planned |
| ST-13 | FT-07 | Merge identity | Planned |
| ST-14 | FT-07 | Merge addresses | Planned |
| ST-15 | FT-07 | Record lineage | Planned |
| ST-16 | FT-08 | Build index | Planned |
| ST-17 | FT-08 | Normalise search fields | Planned |
| ST-18 | FT-09 | Fuzzy search queries | Planned |
| ST-19 | FT-09 | Search ranking | Planned |
| ST-20 | FT-10 | Assemble base profile | Complete |
| ST-21 | FT-10 | Assemble metadata | Planned |
| ST-22 | FT-11 | Expose lineage | Planned |
| ST-23 | FT-11 | Drill-down lineage | Planned |
| ST-24 | FT-12 | Flag conflicts | Planned |
| ST-25 | FT-12 | Show merge logic | Planned |
| ST-26 | FT-13 | Store lineage history | Planned |
| ST-27 | FT-13 | Timestamp lineage | Planned |
| ST-28 | FT-14 | Compute freshness | Planned |
| ST-29 | FT-14 | Compute completeness | Planned |
| ST-30 | FT-15 | Audit ingestion | In Progress |
| ST-31 | FT-15 | Audit merge | Planned |
| ST-32 | FT-16 | Search API basic | Planned |
| ST-33 | FT-16 | Search API ranking | Planned |
| ST-34 | FT-17 | Profile API basic | Planned |
| ST-35 | FT-17 | Profile API lineage | Planned |
