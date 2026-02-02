# Known Issue: Missing Native CLI

**ID**: KI-20260121-native-cli-impl
**Date**: 2026-01-21

## Symptom

Users cannot execute Agent OS commands natively; must use file explorer.

## Root Cause

OS was designed as a "Passive" framework of markdown files.

## Fix

Implemented `agent_cli.py` wrapper.

## verification

Run `./agent_cli.py validate`. Should return GREEN.
