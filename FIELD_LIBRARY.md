# Custom Field Template Registry

The "Custom Field Library" allows users to persist pre-configured questions.

## Data Structure

A template is essentially a named wrapper around a `FormQuestion`.

```json
 {
   "id": "tpl-uuid",
   "name": "NPS Survey",
   "category": "Customer Feedback",
   "question_data": {
     "type": "rating",
     "label": "How likely are you to recommend us?",
     "metadata": {
       "maxStars": 10,
       "icon": "heart"
     }
   }
 }
```

## Backend Implementation

- **Isolation**: Templates belong to a `user_id`.
- **Search**: The `GET /custom-fields` endpoint should allow filtering by `category` and `name`.
- **Injection**: When the frontend asks for a template, the backend serves the `question_data`. The frontend then generates a unique `id` for that specific instance of the question within the form.
