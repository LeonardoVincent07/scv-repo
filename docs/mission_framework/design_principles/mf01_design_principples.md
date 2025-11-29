
# MissionFramework Element: Design Principles

## Overview
High-level architectural principles that guide how all MissionSmith-generated applications are structured and behave.

---

## Codify
- Principles defined in YAML/MD under mission_framework/design_principles.
- Include rules for layering, statelessness, deterministic behaviour, separation of concerns.
- Machine-readable so guardrails and prompts can reference them.

---

## Automate
- Story meta-prompts enforce architectural boundaries.
- CI guardrails check for violations (e.g., direct DB calls, forbidden imports).
- Code generation scaffolds follow these principles by default.

---

## Intercept
- Guardrail engine detects structural violations.
- CI blocks merges that break design principles.
- Warnings raised for non-critical deviations.

---

## Prove
- MissionLog displays design-principle compliance per Story/Feature/Epic.
- Evidence snapshots stored for auditability.

