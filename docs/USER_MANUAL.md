# User Manual: AIOS Form Management System

## 1. Introduction

The AIOS Form Management System allows admins and creators to build dynamic forms, collect employee responses, and analyze data with AI-driven insights. This manual covers core functionalities from a user perspective.

## 2. Getting Started

### 2.1 Access Roles

- **Superadmin/Admin**: Full system control, user management, and global analytics.
- **Creator**: Can build form structures, manage versions, and view responses.
- **Employee**: Can view assigned forms and submit responses.

### 2.2 Accessing the System

Access the system through the primary API gateway or a connected frontend.

- **Authentication**: All users must log in via Email/Password or mobile-based OTP.
- **Session**: Your session is protected by a JWT token. Logging out revokes the session across all devices.

## 3. Key Features

### 3.1 Managing Forms

**Description**: Create and version your form structures.
**Process**:

1. Use the **Form Builder** to defined Sections and Questions.
2. Questions support various types: Text, Rating, File Upload, etc.
3. Manage **Versioning**: Forms are snapshot when published. You can revert to previous versions if needed.

### 3.2 Response Analysis (AI)

**Description**: Automated scanning of submissions.
**How to use**:

1. Select a response in the Dashboard.
2. Trigger **AI Analyze**: Scans for Sentiment and PII (Private Info).
3. Trigger **AI Moderate**: Scans for inappropriate content or security injections.

### 3.3 Workflows

**Description**: Automate actions based on submissions.
**How to use**:

1. Define a **Trigger Form**.
2. Set a **Condition** (e.g., `score > 5`).
3. Select an **Action** (e.g., Create an Approval task or notify another user).

## 4. Troubleshooting

- **Access Denied (403)**: Ensure your role has permission for the requested resource.
- **Session Expired (401)**: Please log in again. Tokens are rotated for security.
- **Missing Data**: Verify that you are looking at the correct **Form Version**.

## 5. FAQ

**Q: Can I delete a published form?**
A: Forms with responses can be archived but not deleted to maintain data integrity.

**Q: How accurate is the Sentiment analysis?**
A: It's a heuristic-based analyzer; for critical business decisions, human review of the flags is recommended.
