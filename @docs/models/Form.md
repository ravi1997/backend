# Form & Response Data Models

## Overview

The data models in AIOS are designed to encapsulate the high complexity of dynamic form definitions while ensuring that response data remains queryable and structured.

## Models

### Form (Document)

**Role**: Global container for a single form entity.
**Key Fields**:

- `title` / `slug`: Human-readable name and URL identifier.
- `status`: Lifecycle state (Draft, Published, Expired).
- `versions`: List of `FormVersion` embedded documents.

### Question (Embedded)

**Role**: Defines an individual question.
**Key Fields**:

- `id`: UUID.
- `label`: Question text.
- `field_type`: Enumerated type (slider, matrix_choice, etc.).
- `meta_data`: Dictionary for field-specific configurations.

## Examples

### Example 1: Slider Question Definition

```json
{
  "id": "q-slider-123",
  "label": "Overall Satisfaction",
  "field_type": "slider",
  "meta_data": {
    "min": 0,
    "max": 10,
    "step": 0.5
  }
}
```

### Example 2: Matrix Choice Question Definition

```json
{
  "id": "q-matrix-456",
  "label": "Rate our service areas",
  "field_type": "matrix_choice",
  "meta_data": {
    "rows": ["Technical Support", "Billing", "Response Time"],
    "columns": ["Poor", "Fair", "Good", "Excellent"]
  }
}
```

### Example 3: Form Response Data

Responses are stored in a hierarchical structure mapping section IDs to question IDs.

```json
{
  "section_main": {
    "q-slider-123": 8.5,
    "q-matrix-456": {
      "Technical Support": "Good",
      "Billing": "Excellent",
      "Response Time": "Fair"
    }
  }
}
```

---
*Technical Note: All models use non-binary UUIDs as primary keys.*
