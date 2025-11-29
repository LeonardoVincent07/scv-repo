
# MissionFramework Element: Analytics

## Overview
Lightweight telemetry and metrics to track behaviour, performance, and usage.

---

## Codify
- Define minimal analytics schema (events, metrics, identifiers).
- Store in mission_framework/analytics.

---

## Automate
- Code generation emits basic telemetry hooks.
- Logging patterns conform to schema.

---

## Intercept
- CI checks for missing telemetry hooks where required.
- Static analysis flags invalid schemas.

---

## Prove
- MissionAtlas (or simple dashboards) surface key metrics.
- MissionLog stores analytics evidence snapshots.

