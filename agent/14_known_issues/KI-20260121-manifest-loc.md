# Known Issue: Manifest Location Ambiguity

**ID**: KI-20260121-manifest-loc
**Date**: 2026-01-21

## Symptom

Master prompt referenced `agent/AGENT_MANIFEST.md` but file was at root. Tools confused.

## Root Cause

Incomplete migration during initial bootstrap.

## Fix

Moved file to `agent/`. Updated `agent_cli.py`.

## Verification

`./agent_cli.py status` prints manifest details correctly.
