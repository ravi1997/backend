# Plan Output Contract: Status Schema

## Purpose

Standardizes the "Status" labels used in headers and state files.

## Valid States

- `DRAFT`: Being written, not ready for review.
- `REVIEW`: Ready for human or peer review.
- `REJECTED`: Rejected by User; requires redo.
- `APPROVED`: Signed off; ready for the next phase.
- `STALE`: Documentation that is no longer accurate to the code.
- `FINAL`: Static document that won't change (e.g., Release Notes).

## Usage

Every plan file must include a `Status: [VALUE]` field in its header.
