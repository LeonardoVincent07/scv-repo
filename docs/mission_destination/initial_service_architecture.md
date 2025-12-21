# Initial Service Architecture (SCV)

**MissionDestination**  
**Single Client View (SCV)**

---

## 1. Purpose

This document defines the **initial service architecture** for the Single Client View (SCV) application.

It establishes:
- the set of services that exist within the SCV domain
- the responsibilities and boundaries of each service
- rules governing data access and service interaction

This artefact represents **global design intent** and is:
- story-agnostic
- stable across the MVP
- authoritative for code placement and responsibility boundaries

It is consumed by:
- story meta-prompts
- test meta-prompts
- human and agent developers

---

## 2. Architectural Principles

1. **Single ownership of responsibility**  
   Each domain responsibility belongs to exactly one service.

2. **Explicit service boundaries**  
   Services interact only through defined APIs.

3. **Controlled database access**  
   Only services explicitly designated may access the database directly.

4. **No architectural redefinition at story level**  
   Stories are implemented within this architecture; they do not redefine it.

---

## 3. Services

### 3.1 Profile Service

**Responsibilities**
- Assemble and expose the canonical client profile
- Apply deterministic profile assembly logic
- Serve profile-related APIs

**Data access**
- Direct read access to client-related tables

**Does not perform**
- Matching
- Merging
- Search indexing
- Ingestion

---

### 3.2 Matching Service

**Responsibilities**
- Determine equivalence between client records
- Produce match decisions and confidence signals

**Data access**
- Direct read access to relevant tables

---

### 3.3 Ingestion Service

**Responsibilities**
- Ingest data from upstream source systems
- Persist raw payloads
- Maintain source system boundaries

**Data access**
- Direct write and read access to ingestion tables

---

### 3.4 Search Service

**Responsibilities**
- Build and maintain search indices
- Execute search queries and ranking logic

**Data access**
- Direct read access to indexed data

---

### 3.5 Lineage and Quality Service

**Responsibilities**
- Track data provenance
- Compute and persist data quality metrics

**Data access**
- Direct read and write access to lineage and quality tables

---

### 3.6 Backend for Frontend (BFF)

**Responsibilities**
- Aggregate backend service responses for frontend consumption
- Adapt backend APIs to frontend needs

**Constraints**
- Performs no business logic
- Performs no data assembly

**Data access**
- No direct database access

---

## 4. Service Interaction Rules

- Services communicate exclusively via APIs
- Services must not access tables owned by other services
- The BFF must not:
  - perform joins
  - apply business rules
  - compute quality or lineage

---

## 5. Change Control

- This document is expected to remain stable through the MVP
- Changes require explicit architectural justification
- All downstream artefacts must be validated against updates

---

**End of document**




