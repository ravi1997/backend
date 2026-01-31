# AI Capabilities API

## Overview

The AI Capabilities module integrates state-of-the-art Large Language Model (LLM) logic directly into the form management process. It provides a suite of advanced features including **Automated Form Generation** from natural language prompts, **Sentiment Analysis** for qualitative feedback, and **Basic/Deep Content Moderation**. The module can scan submissions for **Personally Identifiable Information (PII)** like emails and phone numbers, detect **statistical anomalies** or duplicate spam, and translate Natural Language queries into precise database filters. This ensures that the AIOS platform is not just a data collection tool, but an intelligent assistant helping organizations extract maximum value and security from their data.

## Base URL

`/form/api/v1/ai`

## Endpoints

### POST /generate

**Description**: Generates a complete form structure (sections and questions) based on a natural language prompt.
**Auth Required**: Yes
**Request Body**:

```json
{
  "prompt": "Create a customer satisfaction survey for a coffee shop including coffee quality, staff friendliness, and overall atmosphere.",
  "current_form": {}
}
```

**Examples**:

1. **New Form Concept**: Quickly scaffold a complex survey from a single sentence.
2. **Educational Aid**: Generate forms for specific industrial standards (e.g., ISO compliance).
3. **Contextual Addition**: Provide an existing form to get suggestions for new sections.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/generate \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Employee exit interview form"}'
```

**Expected Output**:

```json
{
  "message": "Form generated successfully",
  "suggestion": {
    "title": "Employee Exit Interview",
    "sections": [...]
  }
}
```

---

### POST /<form_id>/responses/<response_id>/analyze

**Description**: Performs sentiment analysis and PII (Personally Identifiable Information) detection on a specific form submission.
**Auth Required**: Yes
**Examples**:

1. **Sentiment Tagging**: Automatically tag customer reviews as Positive/Negative.
2. **Privacy Audit**: Scan responses for sensitive data before sharing with third parties.
3. **PII Reduction**: Detect phone numbers and emails in open-text fields.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/60d.../responses/60d.../analyze \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "message": "AI analysis complete",
  "results": {
    "sentiment": {"label": "positive", "score": 3, "analyzed_at": "..."},
    "pii_scan": {"found_count": 1, "details": {"emails": ["test@test.com"]}}
  }
}
```

---

### POST /<form_id>/search

**Description**: Translates a natural language search query into an executable database filter and returns the matching response IDs.
**Auth Required**: Yes
**Request Body**:

```json
{
  "query": "Find all patients who are older than 60 and mentioned 'pain' in their feedback."
}
```

**Examples**:

1. **Semantic Search**: Query data using everyday language instead of complex UI filters.
2. **Demographic Filter**: "Find users from last week who were unhappy."
3. **Keyword Insight**: "Show me anyone who brought up 'security issues'."

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/60d.../search \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"query": "older than 25 with high priority"}'
```

**Expected Output**:

```json
{
  "query": "older than 25 with high priority",
  "count": 5,
  "results": ["60d...", "60e...", ...]
}
```

---

### POST /<form_id>/anomalies

**Description**: Scans all responses in a form for statistical outliers, duplicates (spam), and low-quality gibberish.
**Auth Required**: Yes
**Examples**:

1. **Spam Detection**: Identify identical submissions from the same source.
2. **Data Quality**: Flag nonsensical text inputs (e.g., "asdfghjkl").
3. **Outlier Flagging**: Highlight numerical responses that are 2+ standard deviations from the mean.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/60d.../anomalies \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "form_id": "60d...",
  "total_scanned": 150,
  "anomaly_count": 2,
  "anomalies": [
    {
      "response_id": "60d...",
      "type": "outlier",
      "confidence": 0.85,
      "reason": "Value 999 is a statistical outlier for field age"
    }
  ]
}
```

---
*Note: Sentiment Analysis uses a sophisticated local dictionary-based engine, while Form Generation utilizes advanced LLM integration from the AIService.*
