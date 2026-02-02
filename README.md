# AIOS Advanced Form Management Backend

**Version**: 1.1.0  
**Status**: Development  
**License**: Proprietary

---

## 📖 Overview

The AIOS Backend is a robust, scalable, and AI-native form management engine built using **Flask**, **MongoDB**, and **JWT-based Authentication**. It enables organizations to create complex, dynamic forms with advanced validation, AI-driven analysis, and automated workflows.

---

## ✨ Features

- **Dynamic Form Engine**: Support for hierarchical sections, conditional logic, and versioning.
- **AI-Powered Insights**: Automated sentiment analysis, PII detection, and form generation via local LLM (Ollama).
- **Automated Workflows**: Trigger-based actions and approval processes.
- **Secure RBAC**: Granular Role-Based Access Control and secure session management with JWT blocklisting.
- **Analytics**: Real-time tracking and exportable reporting.

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.12+
- **Database**: MongoDB 6.0+
- **AI Provider**: Ollama (optional, for AI features)
- **Docker**: For containerized deployment

### Installation

```bash
# Clone the repository
git clone [repository-url]
cd backend

# Install dependencies (using virtual environment)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local settings (MongoDB URI, Secret keys)
```

### Running the Application

```bash
# Start the development server
python run.py
```

---

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)**: Server setup and environment variables.
- **[User Manual](docs/USER_MANUAL.md)**: Guide for managing forms and responses.
- **[API Documentation](docs/routes/README.md)**: Detailed endpoint definitions and examples.
- **[Architecture](plans/Architecture/OVERVIEW.md)**: System design and ERD.

---

## 🛠️ Configuration

Refer to [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for a full list of environment variables.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run authentication tests
pytest tests/test_auth.py tests/test_auth_edge_cases.py
```

---

## 🏗️ Project Structure

```
backend/
├── app/              # Main application logic
│   ├── routes/       # API Blueprints
│   ├── models/       # MongoDB Models
│   └── utils/        # Shared decorators and helpers
├── tests/            # Automated test suite
├── docs/             # Technical documentation
├── plans/            # Strategic roadmaps and architecture
├── logs/             # Application logs
└── run.py            # Entry point
```

---

## 🗺️ Roadmap

See **[plans/ROADMAP.md](plans/ROADMAP.md)** for planned features and improvements.

---

**Last Updated**: 2026-02-02  
**Maintained By**: Antigravity AI Team
