# Analytics & Export API

## Overview

The Analytics & Export module provides a comprehensive suite of tools for data visualization and reporting, transforming raw form responses into actionable insights. It includes endpoints for calculating **High-Level Summaries** (e.g., total submissions and status breakdowns), **Timeline Trends** (volume over time), and **Statistical Distributions** for choice-based questions (e.g., Pie charts / Bar charts data). The module is designed to handle hierarchical and repeatable sections efficiently, aggregating data across multiple submissions to show frequency and averages. Additionally, it supports **bulk data extraction** via specialized CSV/Excel export endpoints (documented in Export API), making it easy to move data into external business intelligence tools.

## Base URL

`/form/api/v1/form`

## Endpoints

### GET /<form_id>/analytics/summary

**Description**: Returns a top-level snapshot of the form's performance, including total response counts and a breakdown by status.
**Auth Required**: Yes
**Examples**:

1. **Dashboard Widget**: Power a "Total Submissions" counter on the admin home page.
2. **Health Check**: See how many responses are 'Pending' versus 'Approved'.
3. **Activity Tracking**: Check the timestamp of the very last submission received.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f.../analytics/summary \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "total_responses": 150,
  "status_breakdown": {
    "approved": 120,
    "pending": 25,
    "rejected": 5
  },
  "last_submitted_at": "2024-02-15T10:30:00.000Z"
}
```

---

### GET /<form_id>/analytics/timeline

**Description**: Provides a time-series dataset of submission volume over a specified period.
**Auth Required**: Yes
**Query Parameters**:

- `days` (Default: 30): The number of past days to include in the timeline.
**Examples**:

1. **Trend Awareness**: Visualize the daily submission rate for the last month.
2. **Peak Detection**: Identify specific days with unusually high or low activity.
3. **Comparison**: Compare current week's volume against the historical average.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f.../analytics/timeline?days=7 \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "period_days": 7,
  "timeline": [
    {"date": "2024-02-09", "count": 12},
    {"date": "2024-02-10", "count": 15},
    ...
  ]
}
```

---

### GET /<form_id>/analytics/distribution

**Description**: Aggregates answers for choice-based questions (Radio, Select, Checkbox, Rating) into frequency counts.
**Auth Required**: Yes
**Examples**:

1. **Results Visualization**: Generate data for a pie chart showing 'Gender' distribution.
2. **Satisfaction Tracking**: View the count of each rating (1-5) for a specific question.
3. **Option Performance**: See which dropdown options are selected most frequently.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f.../analytics/distribution \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "distribution": [
    {
      "question_id": "q1",
      "label": "Favorite Coffee?",
      "type": "select",
      "counts": {
        "Latte": 45,
        "Espresso": 30,
        "Mocha": 25
      }
    }
  ]
}
```

---
*Note: Distribution logic recursively traverses repeatable sections to ensure every answer is counted accurately.*
