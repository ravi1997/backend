# Form Management System - Backend API

**Version**: 1.0.0  
**Status**: Production  
**License**: MIT  

---

## 📖 Overview

A comprehensive backend API for the **Agent OS Form Builder** that enables organizations to create, manage, and collect responses from dynamic forms with support for complex field types, conditional logic, role-based access control, and external integrations.

The system provides RESTful APIs for form management, user authentication, response collection, and data export, built on Flask with MongoDB as the primary database.

---

## ✨ Features

- **User Authentication & Authorization**: JWT-based authentication with password and OTP support, role-based access control (RBAC)
- **User Management**: Full CRUD operations for users with account locking/unlocking capabilities
- **Form Builder**: Dynamic form creation with sections, questions, multiple field types, and validation rules
- **Form Versioning**: Version history tracking for forms with the ability to roll back or compare versions
- **Response Collection**: Validated form submissions with file upload support
- **Data Export**: Export collected data in CSV and JSON formats
- **Dashboard & Analytics**: Response counts, submission tracking, and workflow automation
- **External Integrations**: Built-in support for UHID (eHospital) API and SMS OTP gateways
- **AI/LLM Integration**: Optional Ollama integration for AI-powered form features

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB 6.0+
- Docker & Docker Compose (recommended)
- Make (optional, for development commands)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start with Docker Compose**

   ```bash
   # Development mode with hot-reloading
   make up-dev
   
   # Production mode
   docker compose up -d
   ```

4. **Access the API**
   - API Base URL: `http://localhost:5000/form/api/v1`
   - Health Check: `http://localhost:5000/`

**For detailed setup instructions**, see:

- [QUICK_START.md](QUICK_START.md) - Get started in 5 minutes
- [GETTING_STARTED.md](GETTING_STARTED.md) - Comprehensive setup guide

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [User Guide](@docs/) | How to use the Form Builder API |
| [API Documentation](route_documentation.md) | Complete API endpoints reference |
| [Architecture](agent/ARCHITECTURE.md) | System design and architecture diagrams |
| [SRS](SRS.md) | Software Requirements Specification |
| [Docker Setup](README_DOCKER.md) | Docker deployment and commands |

---

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Application environment | `development` | No |
| `SECRET_KEY` | Flask secret key | - | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | - | Yes |
| `MONGODB_DB` | MongoDB database name | `ai_backend` | Yes |
| `MONGODB_HOST` | MongoDB host | `localhost` | Yes |
| `MONGODB_PORT` | MongoDB port | `27017` | Yes |
| `MONGODB_USER` | MongoDB username | - | No |
| `MONGODB_PASS` | MongoDB password | - | No |
| `MONGODB_AUTH_SOURCE` | MongoDB auth source | `admin` | No |
| `UPLOAD_FOLDER` | File upload directory | `uploads` | No |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes) | `10485760` | No |
| `LLM_PROVIDER` | LLM provider | `ollama` | No |
| `LLM_API_URL` | LLM API endpoint | `http://ollama:11434/v1` | No |
| `LLM_MODEL` | LLM model name | `llama3` | No |

### Configuration Files

- `.env`: Environment-specific settings (create from `.env.example`)
- `pyproject.toml`: Python project configuration and tooling
- `docker-compose.yml`: Docker services configuration
- `docker-compose.dev.yml`: Development overrides

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with pytest directly
pytest

# Generate coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

Test configuration is defined in `pytest.ini` and `pyproject.toml`.

---

## 📦 Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### Production Deployment

```bash
# Build production image
docker build -t form-backend .

# Run with production settings
docker run -p 5000:5000 --env-file .env form-backend
```

### Manual Deployment

1. Install Python dependencies: `pip install -r requirements.txt`
2. Set environment variables in `.env`
3. Start MongoDB
4. Run: `gunicorn --bind 0.0.0.0:5000 --timeout 120 run:app`

**See [README_DOCKER.md](README_DOCKER.md)** for detailed deployment instructions, troubleshooting, and common commands.

---

## 🏗️ Project Structure

```
backend/
├── app/                    # Main application source code
│   ├── routes/            # API route handlers
│   ├── models/            # MongoDB models (MongoEngine)
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions
│   └── config.py          # Application configuration
├── tests/                 # Test files
├── uploads/               # Uploaded files directory
├── logs/                  # Application logs
├── agent/                 # Agent OS configuration
├── @docs/                 # Documentation
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker services
├── pyproject.toml         # Python project config
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](agent/07_templates/LICENSE.template.md) file for details.

---

## 🗺️ Roadmap

- [ ] Enhanced form validation rules
- [ ] Multi-language form support
- [ ] Advanced analytics dashboard
- [ ] Webhook notifications for form submissions
- [ ] Plugin system for custom field types
- [ ] Enhanced AI-powered features
- [ ] Performance optimization for large-scale deployments

---

**Last Updated**: February 2026  
**Maintained By**: Agent OS Team
