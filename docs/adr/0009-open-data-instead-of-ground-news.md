# ADR-0009 — Rebuild "blindspot" news from GDELT + MBFC instead of Ground News

Date: 2026-09-24 · Status: accepted

## Context
Ground News has no public API; only scrapers exist and personal feeds are not exportable. GDELT DOC 2.0 is free and keyless; MBFC provides outlet bias/factuality via a limited API tier or CSV; AllSides is paid.

## Decision
Use GDELT for coverage/candidates, MBFC for outlet ratings (user-overridable), embedding clustering for stories, and compute a blindspot score locally. Support optional CSV imports (AllSides, community PT-BR list).

## Consequences
+ ToS-clean, open, attributable.
− PT-BR outlet coverage is weak initially.
