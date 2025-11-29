# Technology Guardrails
## MissionFramework

### 1. Purpose
This document defines the mandatory technology constraints for all implementations within this MissionSmith application. These guardrails ensure consistency, predictability, auditability, and safe automation across all Story implementations.

---

## 2. Language and Framework Constraints
- Python is the primary implementation language.
- Only standard library + explicitly approved libraries may be used.
- No dynamic code generation at runtime.
- No reflection-based manipulation of internal structures.

---

## 3. Architectural Layering Rules

### 3.1 Domain Layer Rules (Canonical Logical Data Model)
**All services MUST operate using the canonical Logical Data Model (LDM).**
- Domain logic MUST construct, read, and write typed domain objects defined in `src/domain/models/`.
- Services MUST NOT return dictionaries, JSON, or ad-hoc structures.
- Domain objects are the single internal representation of business truth.

### 3.2 API Representation Rules
**APIs are the ONLY layer permitted to serialise domain models.**
- API slices MAY convert domain objects to dict/JSON.
- API slices MUST NOT contain business logic.
- API slices MUST NOT mutate domain semantics.

### 3.3 No Bypassing Rule
- No slice may bypass services and interact directly with raw upstream payloads.
- Domain entities MUST NOT be constructed directly in API or adapter layers.
- All transformations MUST flow through services.

---

## 4. Implementation Slice Rules
- Each Story is implemented in exactly one code slice.
- A code slice corresponds to a single Python file in the appropriate folder.
- No Story is allowed to modify more than one slice.
- No cross-slice coupling except through domain models.
- No circular imports.

---

## 5. Testing Guardrails
- Tests MUST be deterministic.
- Tests MUST be written using the test meta-prompt.
- Tests MUST verify domain behaviour, not presentation layer behaviour.
- Every Story MUST include:
  - Positive tests
  - Negative tests
  - Edge-case tests
  - Compliance with MissionFramework rules

---

## 6. CI/CD Enforcement Rules
- CI MUST run all tests for every push.
- CI MUST enforce formatting and linting.
- CI MUST fail if:
  - API implements business logic
  - Domain model is bypassed
  - A Story modifies multiple slices
  - Any guardrail is violated

---

## 7. Security and Safety Rules
- No direct file system access except via approved paths under `tools/`.
- No network calls unless explicitly authorised.
- No outbound or inbound external data inside Story implementations during MVP.

---

## 8. Change Control
- Any change to these guardrails requires:
  - Update to meta-prompts
  - Update to related tests
  - Update to dependency rules if applicable
  - Commit message referencing a Story or refactor item
