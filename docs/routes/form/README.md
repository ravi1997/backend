# Form Engine API Reference

The Form Engine is the core component of the AIOS platform. It manages the creation, data collection, and analysis of all forms in the system.

## Sub-Modules

- **[Form Management](./form.md)**: Standard CRUD and version control for form schemas.
- **[Responses](./responses.md)**: Handling submissions, searching data, and managing response status.
- **[AI Capabilities](./ai.md)**: Levering LLMs for form generation, sentiment analysis, and smart search.
- **[Analytics](./analytics.md)**: Aggregating submission data into summaries, timelines, and distributions.
- **[Export](./export.md)**: Extracting data in CSV, JSON, or Bulk ZIP formats.

## Common Concepts

### Hierarchical Data

Form data is organized by **Section ID** and then **Question ID**.
Example:

```json
{
  "section_888": {
    "question_123": "Answer"
  }
}
```

### Repeatable Sections

Sections marked as `is_repeatable_section` will have their data represented as a **List of Objects** instead of a single Object.
Example:

```json
{
  "section_family": [
    {"name_id": "John", "age_id": 30},
    {"name_id": "Jane", "age_id": 28}
  ]
}
```

### Authorization

Most form operations respect a granular permission system. You must be an **Editor** or **Creator** of a form to modify its structure or see non-aggregated response details.
