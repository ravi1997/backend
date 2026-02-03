# Contributing to Form Management System

Thank you for your interest in contributing to the Form Management System Backend! This document provides guidelines and instructions for contributing to this project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [提交变更](#submitting-changes)
- [Documentation](#documentation)
- [Questions and Support](#questions-and-support)

---

## 🤝 Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- MongoDB 6.0+
- Docker & Docker Compose
- Git

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork locally**

   ```bash
   git clone https://github.com/YOUR-USERNAME/backend.git
   cd backend
   ```

3. **Set up upstream remote**

   ```bash
   git remote add upstream https://github.com/ORIGINAL-USERNAME/backend.git
   ```

4. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

7. **Start MongoDB** (or use Docker)

   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:6.0
   
   # Or use docker compose
   docker compose up -d db
   ```

8. **Verify setup**

   ```bash
   pytest tests/ -v
   ```

---

## 🔄 Development Workflow

### 1. Sync with Upstream

Before starting work, always sync with the upstream repository:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

Follow the coding standards outlined below. Make incremental commits with clear messages.

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v
```

### 5. Run Linters

```bash
# Format code
black .
ruff check --fix .

# Type checking
mypy .
```

### 6. Update Documentation

If you've added new features or changed behavior, update the documentation.

### 7. Submit Changes

```bash
git add .
git commit -m "feat: Add your feature description"
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub.

---

## 📝 Coding Standards

### Python Style

- **Linter**: ruff (configured in `pyproject.toml`)
- **Formatter**: black (120 character line length)
- **Type Hints**: Required for public APIs
- **Docstrings**: Google-style docstrings

### Code Style Rules

```bash
# Format code
black app/ tests/

# Check for issues
ruff check app/ tests/

# Auto-fix issues
ruff check --fix app/ tests/
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `get_user_by_id()` |
| Classes | PascalCase | `FormManager` |
| Constants | UPPER_SNAKE_CASE | `MAX_UPLOAD_SIZE` |
| Private methods | `_single_leading_underscore` | `_validate_input()` |

### MongoDB Models

- Use MongoEngine ODM as defined in the project
- Define indexes for frequently queried fields
- Use proper field validation
- Follow the existing model structure in `app/models/`

### API Design

- Follow RESTful conventions
- Use consistent response formats
- Include proper error handling
- Add appropriate status codes

---

## 🧪 Testing Requirements

### Test Coverage

- All new features must include tests
- Aim for minimum 80% test coverage
- Unit tests for all service functions
- Integration tests for API endpoints

### Writing Tests

```python
# tests/test_auth.py
import pytest
from app.services.auth import authenticate_user

class TestAuthentication:
    """Test authentication service"""
    
    def test_successful_login(self, db_session):
        """Test user can login with valid credentials"""
        user = create_test_user()
        result = authenticate_user(user.email, "validpassword")
        assert result is not None
        assert result.id == user.id
    
    def test_invalid_password(self, db_session):
        """Test login fails with invalid password"""
        user = create_test_user()
        result = authenticate_user(user.email, "wrongpassword")
        assert result is None
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_form_service.py

# With verbose output
pytest -v

# With coverage report
pytest --cov=app --cov-report=html

# Watch mode (development)
ptw  # pytest-watch
```

### Test Fixtures

Use `conftest.py` for shared fixtures. Common fixtures:

- `db_session`: Database session for tests
- `test_user`: Create a test user
- `auth_token`: JWT token for authenticated requests
- `test_form`: Create a test form

---

## 📤 Submitting Changes

### Pull Request Guidelines

1. **Title**: Clear, concise summary of changes
2. **Description**: Detailed explanation of what changed and why
3. **Checklist**:
   - [ ] Tests pass
   - [ ] Linters pass
   - [ ] Documentation updated
   - [ ] No merge conflicts
4. **Screenshots**: If UI changes, include screenshots

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:

```
feat(auth): Add password reset functionality

Implement password reset via email OTP for users who forgot their password.
Includes rate limiting to prevent abuse.

Closes #123
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your PR will be merged
4. Thank you for your contribution!

---

## 📚 Documentation

### Code Documentation

- Write docstrings for all public functions and classes
- Include type hints
- Add examples for complex functions

### API Documentation

- Update `route_documentation.md` for new endpoints
- Include request/response examples
- Document error responses

### README Updates

- Update README.md if adding new features
- Update Quick Start if setup changed

---

## ❓ Questions and Support

- **Issues**: Open a GitHub Issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for sensitive issues

---

## 📖 Additional Resources

- [Project README](README.md)
- [API Documentation](route_documentation.md)
- [SRS Documentation](SRS.md)
- [Architecture Guide](agent/ARCHITECTURE.md)
- [Docker Setup](README_DOCKER.md)

---

**Thank you for contributing to the Form Management System!**
