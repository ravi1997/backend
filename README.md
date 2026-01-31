# Form Builder Backend - Project Overview

## Introduction

This backend is designed to support a high-performance, dynamic form builder application. It manages form configurations (JSON-based layout), user-defined field templates, form versioning, and respondent submissions.

## Core Technologies (Recommended)

- **Runtime**: Node.js (TypeScript) / Go / Python (FastAPI)
- **Database**: PostgreSQL (with JSONB support) or MongoDB
- **Cache**: Redis (for session management and rate limiting)
- **Storage**: AWS S3 or Google Cloud Storage (for images and signatures)

## Key Challenges

1. **Dynamic Schema**: The form structure is recursive and deeply nested (Sections -> Questions -> Metadata).
2. **Metadata Consistency**: Advanced fields like Matrix Choice and Rating rely on custom JSON keys in the `metadata` field.
3. **Form Versioning**: Snapshooting forms when published to ensure submissions are linked to the correct form version.

## Documentation Structure

- `/docs/schema/DATABASE_SCHEMA.md`: Data models and relationships.
- `/docs/api/ENDPOINTS.md`: REST API specifications for the builder.
- `/docs/api/SUBMISSIONS.md`: Validation and storage of respondent data.
- `VERSIONING.md`: Strategy for form versioning and snapshots.
- `FIELD_LIBRARY.md`: Implementation of the custom field template registry.
