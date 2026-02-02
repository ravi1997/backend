# Functional Requirements (Reconstructed from Reality)

## 1. Overview

The Form Management System Backend provides a RESTful API for dynamic form creation, versioning, response collection, and AI-driven analysis.

## 2. User Stories

| ID | Role | Feature | Reason | Status |
|---|---|---|---|---|
| US-01 | Creator | Create/Manage Forms | To collect data from users dynamically | IMPLEMENTED |
| US-02 | Employee | Submit Responses | To report data to the organization | IMPLEMENTED |
| US-03 | Admin | Manage Users/Roles | To control access to forms and data | IMPLEMENTED |
| US-04 | Analyst | Analyze Responses | To derive insights using AI tools | IMPLEMENTED |
| US-05 | Manager | Export Data | To process data in external tools (Excel) | IMPLEMENTED |

## 3. Core Features

### 4.1 Authentication & Authorization

- **JWT-based Authentication**: Secure access to all API endpoints.
- **OTP Login**: Mobile-based login for easy access.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions (Admin, Creator, Editor, etc.).

### 4.2 Dynamic Form Builder

- **Flexible Schema**: Support for Sections and Questions.
- **Multiple Field Types**: Text, Number, Date, Select, Radio, Checkbox, Rating, File Upload.
- **Conditional Logic**: Visibility conditions and custom validation rules.
- **Versioning**: Maintain multiple versions of a form with easy rollback/activation.

### 4.3 Response Collection

- **Validated Submissions**: Ensures data integrity based on form rules.
- **Draft Support**: Save and resume submissions.
- **Response History**: Track changes to submissions over time.

### 4.4 AI & Analytics

- **Sentiment Analysis**: Automated sentiment detection on text responses.
- **PII & Moderation**: Scan for sensitive info and inappropriate content.
- **Anomaly Detection**: Identify outliers and spam.
- **Natural Language Search**: Query responses using plain English.

### 4.5 Workflows

- **Trigger Actions**: Automate tasks based on form submissions.
- **Status Tracking**: Approval workflows and status logs.

## 4. Edge Cases

- **Expired Password**: Enforce password change after 90 days.
- **Account Locking**: Protect against brute-force attacks after 5 failed attempts.
- **Duplicate Prevention**: Statistical/AI-based duplicate detection for submissions.
