# Example: Feature Delivery

This example shows a complete feature delivery workflow from request to PR.

## Scenario

**User requests:** "implement feature: user login with email and password"

---

## Step 1: Agent Reads Router

Agent reads `00_INDEX.md` and identifies this as:
- **Type:** Feature / task
- **Trigger keyword:** "implement feature"
- **Route to:** `workflows/feature_delivery.md`

---

## Step 2: Fill Feature Form

Agent fills `forms/FEATURE_MIN.md`:

```markdown
1) Feature name: User Login with Email/Password
2) User story: As a user, I want to log in with my email and password so that I can access my pledge information
3) Acceptance criteria:
   - User can enter email and password
   - System validates credentials
   - Successful login redirects to dashboard
   - Failed login shows error message
   - Session persists across page refreshes
4) Dependencies: None
5) Estimated complexity: Medium (2-3 hours)
```

---

## Step 3: Create Implementation Plan

Agent creates `artifacts/DECISION_RECORD.md`:

```markdown
# Decision Record: User Login Implementation

## Context
Need to add email/password authentication to allow users to access their pledge information.

## Decision
Implement Flask-Login based authentication with:
- Email/password storage (hashed with bcrypt)
- Session management
- Login/logout routes
- Protected dashboard route

## Alternatives Considered
1. OAuth only (rejected - too complex for initial release)
2. Magic link login (rejected - users prefer password)
3. Flask-Security (rejected - too heavyweight)

## Implementation Plan

### 1. Database Changes
- Add `User` model with email, password_hash fields
- Migration to create users table

### 2. Authentication Routes
- `/login` (GET/POST) - Login form and handler
- `/logout` (POST) - Logout handler
- `/register` (GET/POST) - Registration form and handler

### 3. Protected Routes
- Update `/dashboard` to require login
- Redirect to login if not authenticated

### 4. Templates
- `login.html` - Login form
- `register.html` - Registration form
- Update `base.html` with login/logout links

### 5. Tests
- Test user registration
- Test login success/failure
- Test logout
- Test protected route access
```

---

## Step 4: Implementation

### 4.1: Database Model

```python
# app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### 4.2: Authentication Routes

```python
# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html')
```

### 4.3: Protected Routes

```python
# app/routes/main.py
from flask_login import login_required

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
```

### 4.4: Database Migration

```bash
# Create migration
flask db migrate -m "Add User model for authentication"

# Review migration file
# alembic/versions/abc123_add_user_model.py

# Apply migration
flask db upgrade
```

---

## Step 5: Testing

Agent creates tests following `testing/TEST_STRATEGY.md`:

```python
# tests/test_auth.py
import pytest
from app.models import User
from app import db

def test_user_registration(client):
    """Test user can register with email and password"""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    # Verify user in database
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.check_password('SecurePass123')

def test_user_login_success(client, test_user):
    """Test user can login with correct credentials"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'dashboard' in response.data.lower()

def test_user_login_failure(client):
    """Test login fails with incorrect credentials"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert b'Invalid email or password' in response.data

def test_logout(client, authenticated_client):
    """Test user can logout"""
    response = authenticated_client.post('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'logged out' in response.data.lower()

def test_protected_route_requires_login(client):
    """Test dashboard requires authentication"""
    response = client.get('/dashboard', follow_redirects=True)
    
    assert b'login' in response.data.lower()

@pytest.fixture
def test_user(app):
    """Create a test user"""
    user = User(email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    """Client with authenticated session"""
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    return client
```

---

## Step 6: Quality Gates

Agent runs `gates/QUALITY_GATES.md`:

```bash
# Run tests
pytest -v tests/test_auth.py
# Output: 5 passed

# Run linter
ruff check app/routes/auth.py app/models.py tests/test_auth.py
# Output: All checks passed

# Run formatter
ruff format app/routes/auth.py app/models.py tests/test_auth.py
# Output: 3 files reformatted

# Check test coverage
pytest --cov=app.routes.auth tests/test_auth.py
# Output: 95% coverage
```

All gates passed ✅

---

## Step 7: Generate PR Summary

Agent creates `artifacts/pr_summary.md`:

```markdown
# PR Summary: User Login with Email/Password

## Changes
Implemented email/password authentication using Flask-Login.

### Files Added
- `app/routes/auth.py` - Authentication routes (login, logout, register)
- `app/templates/login.html` - Login form
- `app/templates/register.html` - Registration form
- `tests/test_auth.py` - Authentication tests
- `alembic/versions/abc123_add_user_model.py` - User table migration

### Files Modified
- `app/models.py` - Added User model
- `app/__init__.py` - Registered auth blueprint, configured Flask-Login
- `app/templates/base.html` - Added login/logout links
- `app/routes/main.py` - Protected dashboard route
- `requirements.txt` - Added flask-login, bcrypt

## Testing
- ✅ 5 new tests added
- ✅ All tests passing
- ✅ 95% code coverage
- ✅ Linter passed
- ✅ Manual testing completed

## Security Considerations
- Passwords hashed with bcrypt
- CSRF protection enabled
- Session cookies secure and httponly
- Login rate limiting (via existing Flask-Limiter)

## Migration Required
```bash
flask db upgrade
```

## Deployment Notes
- No environment variables needed
- Database migration required before deployment
- Backward compatible (existing routes unchanged)

## Screenshots
(Would include screenshots of login/register forms)

## Checklist
- [x] Code follows project conventions
- [x] Tests added and passing
- [x] Documentation updated
- [x] Security review completed
- [x] Migration tested
- [x] Ready for review
```

---

## Total Time

- **Planning:** 10 minutes
- **Implementation:** 45 minutes
- **Testing:** 20 minutes
- **Documentation:** 10 minutes
- **Total:** ~1.5 hours

---

## Key Takeaways

1. **Structured approach:** Form → Plan → Implement → Test → Document
2. **Quality gates:** All tests and lints passed before PR
3. **Security first:** Password hashing, CSRF protection
4. **Complete documentation:** Decision record + PR summary
5. **Test coverage:** 95% coverage with comprehensive tests
