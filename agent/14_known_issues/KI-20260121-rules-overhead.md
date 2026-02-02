# Known Issue: High Cognitive Load

**ID**: KI-20260121-rules-overhead
**Date**: 2026-01-21

## Symptom

Full rule set > 2k tokens, causing forgetting in small context windows.

## Root Cause

Extensive documentation in `00_system`.

## Fix

Created `00_core_rules_lite.md` (<100 tokens).

## Verification

Checked file existence and content brevity.
