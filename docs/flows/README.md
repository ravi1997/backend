# Business Flows Documentation

This section explains the core logical processes of the AIOS Backend. Understanding these flows is essential for understanding how different API modules interact to achieve complex business goals.

## Core Flows

### 1. [Authentication & Security](./auth_flow.md)

Discover how the system handles user identity, secure sessions (JWT), and automated protection like account lockout and password expiration.

### 2. [Form Lifecycle & Versioning](./form_lifecycle.md)

Learn about the journey of a form from Draft to Published and how versioning allows for seamless updates without data loss.

### 3. [Submission & Validation](./submission_flow.md)

A deep dive into how user input is processed, validated against complex rules, and safely stored in the database.

### 4. [Automated Workflow & Approval](./approval_workflow.md)

Explore the notification, task assignment, and manual approval mechanisms that drive organizational efficiency.

---
*Each document includes a visual Mermaid diagram to illustrate the sequence of events.*
