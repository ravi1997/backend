# Export API

## Overview

The Export module provides essential data portability features, allowing users to extract collected information in high-quality, structured formats compatible with external spreadsheets and analytical tools. It supports **CSV (Comma-Separated Values)** generation with automatic header mapping from form labels, **Deep JSON Export** including full metadata and entire response objects, and **Bulk ZIP Export** for downloading data from multiple forms simultaneously. A standout feature is the intelligent **hierarchical flattening logic**, which correctly handles repeatable sections by concatenating entries using a delimiter (e.g., " | "), ensuring that complex data remains readable and processable in a standard tabular format like Microsoft Excel or Google Sheets.

## Base URL

`/form/api/v1/form`

## Endpoints

### GET /<form_id>/export/csv

**Description**: Generates and streams a CSV file containing all responses for a specified form. Headers are derived from the latest form version's question labels.
**Auth Required**: Yes (View Permission)
**Examples**:

1. **Direct Download**: Click a link to download the current dataset as an Excel-ready file.
2. **External Audit**: Send a snapshot of responses to an auditor in a universal format.
3. **Basic Reporting**: Open the file in Google Sheets for quick sorting and pivoting.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f.../export/csv \
     -H "Authorization: Bearer <token>" \
     -o audit_responses.csv
```

**Expected Output**: A file `audit_responses.csv` containing the response table.

---

### GET /<form_id>/export/json

**Description**: Returns a full JSON dump of the form's metadata and every associated response. This is a lossless export format.
**Auth Required**: Yes
**Examples**:

1. **System Migration**: Export data from one instance to import into another.
2. **Programmatic Processing**: Fetch the entire dataset as JSON for a custom Python/JS script.
3. **Backup**: Store a machine-readable snapshot of the data.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f.../export/json \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "form_metadata": {
    "id": "60d5f...",
    "title": "Quarterly Health Audit",
    ...
  },
  "responses": [
    {"id": "60d...", "data": {...}},
    ...
  ]
}
```

---

### POST /export/bulk

**Description**: Accepts a list of form IDs and generates a ZIP archive containing separate CSV files for each form.
**Auth Required**: Yes
**Request Body**:

```json
{
  "form_ids": ["60d5f1...", "60d5f2...", "60d5f3..."]
}
```

**Examples**:

1. **Multi-Project Export**: Download reports for an entire department's forms in one go.
2. **Periodic Backup**: Bulk export all active forms at the end of the month.
3. **Consolidated Audit**: Gather evidence from multiple distinct data collection streams.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/form/export/bulk \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"form_ids": ["60d1...", "60d2..."]}' \
     -o multi_export.zip
```

**Expected Output**: A ZIP archive `bulk_export_20240215_120000.zip` containing multiple CSV files
---

*Technical Note: Filenames inside the ZIP are sanitized to remove special characters, ensuring compatibility across Windows, MacOS, and Linux systems.*
