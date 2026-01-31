# Field Metadata Specifications

This document defines the expected structure of the `meta_data` field for various question types. Adhering to these specifications ensures consistency between the Frontend Builder and the Backend Engine.

## Field Types

### 1. Rating

Used for collecting numerical scores (e.g., star ratings).
**Metadata Structure**:

```json
{
  "max_stars": 5,
  "icon": "star"
}
```

- `max_stars`: (int) The maximum selectable value.
- `icon`: (string) The name of the icon to display (e.g., "star", "heart").

### 2. Slider

Used for selecting a value within a range.
**Metadata Structure**:

```json
{
  "min": 0,
  "max": 100,
  "step": 1
}
```

- `min`: (number) Minimum selectable value.
- `max`: (number) Maximum selectable value.
- `step`: (number) The increment between values.

### 3. Matrix Choice

Used for grid-style questions where multiple rows share the same column options.
**Metadata Structure**:

```json
{
  "rows": ["Quality", "Speed", "Price"],
  "columns": ["Poor", "Average", "Good", "Excellent"]
}
```

- `rows`: (string[]) Array of row labels.
- `columns`: (string[]) Array of column labels/values.

### 4. Image

Used for displaying static images within the form.
**Metadata Structure**:

```json
{
  "image_url": "https://example.com/logo.png",
  "alt_text": "Company Logo"
}
```

- `image_url`: (string) The full URL to the image.
- `alt_text`: (string) Accessibility description.

---
*Note: The backend uses these metadata values for server-side validation where applicable (e.g., Sliders).*
