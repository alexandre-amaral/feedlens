# ADR-0006 — Probabilities are calibrated post-hoc on the user's own labels; verbalized confidence is never trusted

Date: 2026-09-24 · Status: accepted

## Context
Verbalized confidences and raw softmax from small models are poorly calibrated (arXiv 2608.04899, 2609.10996; jev-on-a-laptop found >0.90 confidence on most wrong answers). TypeSafe's adapter produces verbalized distributions. Jev's own calibration is unverified.

## Decision
Every decision field stores raw probabilities and a `calibrated` flag. Temperature scaling (fallback isotonic) is fitted per field once ≥30 labels exist from explicit feedback. Thresholds for hard actions (e.g. auto-drop on `avoid`) use calibrated values only; before calibration exists, decisions are ranking signals only.

## Consequences
+ Honest confidence in the UI (ECE shown).
− Cold start: first days rely on weights and rules more than on thresholds.
