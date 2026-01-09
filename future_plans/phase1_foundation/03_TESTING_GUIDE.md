# Testing Guide: Phase 1 Foundation
## Comprehensive Testing Strategy

**Phase:** P1 - Foundation  
**Version:** 1.0  

---

## Testing Pyramid

```
       /\
      /E2E\          10% - End-to-End
     /------\
    /  INT   \       30% - Integration  
   /----------\
  /    UNIT    \     60% - Unit Tests
 /--------------\
```

## Test Environment Setup

### Docker Test Environment

**`docker-compose.test.yml`**
```yaml
version: '3.8'
services:
  mongo-test:
    image: mongo:6.0
    ports:
      - "27018:27017"
    tmpfs:
      - /data/db

  redis-test:
    image: redis:7.2-alpine
    ports:
      - "6380:6379"
    tmpfs:
      - /data
```

### Test Configuration

**`tests/conftest.py`**
```python
import pytest
from app import create_app
from app.database import db

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def clean_db():
    for collection in db.list_collection_names():
        db[collection].delete_many({})
    yield db
```

---

## Unit Tests

### Tenant Model Tests

**`tests/unit/test_tenant_model.py`**
```python
def test_create_tenant(clean_db):
    from app.models.Tenant import Tenant
    tenant = Tenant.create({
        'tenant_id': 'org-123',
        'name': 'Test Org'
    })
    assert tenant['tenant_id'] == 'org-123'

def test_tenant_exists(clean_db):
    from app.models.Tenant import Tenant
    Tenant.create({'tenant_id': 'test', 'name': 'Test'})
    assert Tenant.exists('test') is True
    assert Tenant.exists('fake') is False
```

### Event System Tests

**`tests/unit/test_events.py`**
```python
def test_event_emission(app):
    from app.events.signals import response_submitted
    from app.events.event_dispatcher import EventDispatcher
    
    received = []
    
    @response_submitted.connect
    def capture(sender, event_data, **extra):
        received.append(event_data)
    
    EventDispatcher.emit(
        signal=response_submitted,
        entity_id='test-123',
        payload={'data': 'test'}
    )
    
    assert len(received) == 1
    assert received[0]['entity_id'] == 'test-123'
```

---

## Security Tests

### Tenant Isolation

**`tests/security/test_isolation.py`**
```python
def test_cross_tenant_access_denied(app, client):
    """CRITICAL: Verify tenant isolation"""
    # Create form in tenant A
    response = client.post('/api/v1/forms',
        json={'title': 'Form A', 'slug': 'form-a'},
        headers={'X-Tenant-ID': 'tenant-a'})
    form_id = response.json['form_id']
    
    # Try to access from tenant B
    response = client.get(f'/api/v1/forms/{form_id}',
        headers={'X-Tenant-ID': 'tenant-b'})
    
    assert response.status_code == 404
```

---

## Performance Tests

**`tests/performance/test_benchmarks.py`**
```python
def test_submission_performance(benchmark, client):
    def submit():
        return client.post('/api/v1/forms/test/submit',
            json={'name': 'Test'},
            headers={'X-Tenant-ID': 'test'})
    
    result = benchmark(submit)
    assert result.stats['mean'] < 0.1  # <100ms
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Parallel
pytest tests/ -n auto

# Specific category
pytest tests/security/ -v
```

---

## CI/CD Integration

**`.github/workflows/test.yml`**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:6.0
      redis:
        image: redis:7.2-alpine
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest tests/ -v --cov=app
```
