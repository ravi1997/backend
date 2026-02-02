# Known Issue: Broken Prompts

**ID**: KI-20260121-prompt-validation-failures
**Date**: 2026-01-21

## Symptom

Prompts fail validation due to missing headers or pending TODOs.

## Root Cause

Initial content generation created stubs or used non-standard formats.

## Fix

1. Implemented `verify_prompts.py` with flexible regex matching.
2. Updated failing prompts to include required `OUTPUT` sections.
3. Removed `TODO` placeholders or replaced with specific instructions.

## Verification

Run `./tests/prompt_validation/verify_prompts.py`. Should return 0 failures.
