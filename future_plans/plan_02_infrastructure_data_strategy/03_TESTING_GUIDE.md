# Testing Guide
## Plan 2: Infrastructure & Data Strategy

**Version:** 1.0  
**Date:** 2026-01-09  
**Purpose:** Comprehensive testing strategy for infrastructure components

---

## Table of Contents
1. [Testing Strategy](#testing-strategy)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Chaos Testing](#chaos-testing)
8. [Test Automation](#test-automation)
9. [Test Data Management](#test-data-management)
10. [Reporting](#reporting)

---

## Testing Strategy

### Testing Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /----\  
     /      \ Integration Tests (30%)
    /--------\
   /          \ Unit Tests (60%)
  /-----------
-\
```

### Test Types

| Type | Coverage | Frequency | Duration |
|------|----------|-----------|----------|
| Unit | 60% | Every commit | < 5 min |
| Integration | 30% | Every PR | < 15 min |
| E2E | 10% | Pre-deployment | < 30 min |
| Performance | - | Weekly | < 2 hours |
| Security | - | Daily | < 1 hour |
| Chaos | - | Monthly | < 4 hours |

---

## Test Environment Setup

### Prerequisites

```bash
# Install testing tools
pip install pytest pytest-cov pytest-asyncio pytest-mock
pip install locust stress-ng
pip install docker-compose

# Install security tools
pip install safety bandit
docker pull aquasec/trivy

# Install monitoring
pip install prometheus-client
```

### Test Environment Configuration

**File:** `docker-compose.test.yml`

```yaml
version: '3.8'

services:
  test-api:
    build: .
    environment:
      - ENVIRONMENT=test
      - MONGODB_URL=mongodb://test-mongodb:27017/test_db
      - REDIS_URL=redis://test-redis:6379/1
    depends_on:
      - test-mongodb
      - test-redis
    networks:
      - test-network

  test-worker:
    build: .
    command: celery -A app.celery worker --loglevel=info
    environment:
      - ENVIRONMENT=test
      - MONGODB_URL=mongodb://test-mongodb:27017/test_db
      - REDIS_URL=redis://test-redis:6379/1
    depends_on:
      - test-mongodb
      - test-redis
    networks:
      - test-network

  test-mongodb:
    image: mongo:5.0
    tmpfs:
      - /data/db
    networks:
      - test-network

  test-redis:
    image: redis:7-alpine
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

### Starting Test Environment

```bash
# Start test containers
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be healthy
./scripts/wait-for-services.sh

# Run tests
pytest

# Tear down
docker-compose -f docker-compose.test.yml down -v
```

---

## Unit Testing

### Configuration Testing

**File:** `tests/test_config.py`

```python
import pytest
import os
from app.config import get_settings

def test_gunicorn_worker_count():
    """Test Gunicorn worker calculation"""
    from app.gunicorn_config import workers
    import multiprocessing
    
    expected = (2 * multiprocessing.cpu_count()) + 1
    assert workers == expected

def test_celery_routing():
    """Test Celery task routing configuration"""
    from app.celery_config import task_routes
    
    assert 'app.tasks.ai.*' in str(task_routes)
    assert task_routes['app.tasks.ai.*']['queue'] == 'batched'

def test_resource_limits():
    """Test Docker resource limit parsing"""
    from app.utils.resource_limits import parse_cpu_limit
    
    assert parse_cpu_limit('0.5') == 0.5
    assert parse_cpu_limit('2') == 2.0

def test_environment_variables():
    """Test required environment variables"""
    required_vars = [
        'MONGODB_URL',
        'REDIS_URL',
        'SECRET_KEY'
    ]
    
    for var in required_vars:
        assert os.getenv(var) is not None, f"{var} not set"
```

### Task Testing

**File:** `tests/test_tasks.py`

```python
import pytest
from unittest.mock import Mock, patch
from app.tasks.ai import task_generate_response
from app.tasks.email import task_send_email

@pytest.mark.asyncio
async def test_ai_task_execution():
    """Test AI task executes correctly"""
    with patch('app.tasks.ai.model_inference') as mock_inference:
        mock_inference.return_value = "Generated response"
        
        result = await task_generate_response.apply_async(
            args=['Test prompt']
        ).get()
        
        assert result == "Generated response"
        mock_inference.assert_called_once()

def test_task_retry_on_failure():
    """Test task retries on failure"""
    with patch('app.tasks.email.smtp_send') as mock_send:
        mock_send.side_effect = [Exception("Connection failed"), True]
        
        # Should retry and succeed
        result = task_send_email.apply(
            args=['test@example.com', 'Subject', 'Body']
        )
        
        assert result.successful()
        assert mock_send.call_count == 2

def test_task_timeout():
    """Test task respects timeout"""
    import time
    from celery.exceptions import SoftTimeLimitExceeded
    
    @app.task(soft_time_limit=1)
    def slow_task():
        time.sleep(10)
    
    with pytest.raises(SoftTimeLimitExceeded):
        slow_task.apply().get()

def test_task_routing():
    """Test tasks route to correct queues"""
    from app.tasks.ai import task_classify_input
    
    # Check task is routed to batched queue
    assert task_classify_input.queue == 'batched'
```

### Model Testing

**File:** `tests/test_ai_models.py`

```python
import pytest
from app.ai.model_loader import load_model, ModelType

def test_model_loading():
    """Test model loads successfully"""
    model = load_model(ModelType.LLAMA_7B_Q4)
    assert model is not None
    assert model.is_ready()

def test_model_inference():
    """Test model inference"""
    model = load_model(ModelType.LLAMA_7B_Q4)
    
    prompt = "Hello, world!"
    response = model.generate(prompt, max_tokens=10)
    
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.benchmark
def test_inference_speed(benchmark):
    """Benchmark inference speed"""
    model = load_model(ModelType.LLAMA_7B_Q4)
    
    def infer():
        return model.generate("Test prompt", max_tokens=20)
    
    result = benchmark(infer)
    assert benchmark.stats['mean'] < 10.0  # Should be < 10s

def test_model_memory_usage():
    """Test model memory footprint"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    model = load_model(ModelType.LLAMA_7B_Q4)
    
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    mem_used = mem_after - mem_before
    
    assert mem_used < 4096  # Should use < 4GB
```

---

## Integration Testing

### Service Integration Tests

**File:** `tests/integration/test_service_communication.py`

```python
import pytest
import requests
from app import create_app
from celery import Celery

@pytest.fixture(scope='module')
def app():
    """Create test app"""
    return create_app('test')

@pytest.fixture(scope='module')
def client(app):
    """Create test client"""
    return app.test_client()

def test_api_to_database(client):
    """Test API can communicate with database"""
    response = client.post('/api/v1/forms', json={
        'title': 'Test Form',
        'fields': []
    })
    
    assert response.status_code == 201
    assert 'form_id' in response.json

def test_api_to_redis(client):
    """Test API can cache in Redis"""
    # First request - cache miss
    response1 = client.get('/api/v1/forms/123')
    
    # Second request - cache hit
    response2 = client.get('/api/v1/forms/123')
    
    assert response1.json == response2.json
    assert 'X-Cache-Hit' in response2.headers

def test_api_to_celery(client):
    """Test API can queue tasks"""
    response = client.post('/api/v1/forms/123/analyze', json={
        'prompt': 'Analyze this form'
    })
    
    assert response.status_code == 202
    assert 'task_id' in response.json
    
    # Check task was queued
    task_id = response.json['task_id']
    task_status = client.get(f'/api/v1/tasks/{task_id}')
    
    assert task_status.json['status'] in ['PENDING', 'PROCESSING']

def test_worker_to_database():
    """Test worker can access database"""
    from app.tasks.analytics import task_export_data
    
    result = task_export_data.apply().get()
    assert result['exported_count'] >= 0

def test_worker_to_webhook():
    """Test worker can call webhooks"""
    from app.tasks.webhooks import task_send_webhook
    from unittest.mock import patch
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        
        task_send_webhook.apply(args=[
            'https://example.com/webhook',
            {'event': 'test'}
        ]).get()
        
        mock_post.assert_called_once()
```

### End-to-End Tests

**File:** `tests/e2e/test_form_submission_flow.py`

```python
import pytest
import time

def test_complete_form_submission_with_ai(client):
    """Test complete flow: submit form -> AI process -> webhook"""
    
    # Step 1: Create form
    form_response = client.post('/api/v1/forms', json={
        'title': 'AI-Enabled Form',
        'fields': [
            {'name': 'message', 'type': 'text', 'ai_enabled': True}
        ],
        'webhook_url': 'https://webhook.site/test-123'
    })
    form_id = form_response.json['form_id']
    
    # Step 2: Submit response
    submission_response = client.post(
        f'/api/v1/forms/{form_id}/responses',
        json={'message': 'Hello AI!'}
    )
    
    assert submission_response.status_code == 202
    task_id = submission_response.json['task_id']
    
    # Step 3: Wait for AI processing
    max_wait = 30
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status_response = client.get(f'/api/v1/tasks/{task_id}')
        status = status_response.json['status']
        
        if status == 'SUCCESS':
            break
        elif status == 'FAILURE':
            pytest.fail("Task failed")
        
        time.sleep(1)
    
    # Step 4: Verify webhook was called
    # (In real test, use webhook testing service)
    assert status_response.json['webhook_sent'] is True
    
    # Step 5: Verify analytics updated
    analytics_response = client.get(f'/api/v1/forms/{form_id}/analytics')
    assert analytics_response.json['total_responses'] == 1
```

---

## Performance Testing

### Load Testing with Locust

**File:** `tests/performance/locustfile.py`

```python
from locust import HttpUser, task, between

class FormUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before tests"""
        response = self.client.post('/api/v1/auth/login', json={
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.token = response.json()['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    @task(3)
    def list_forms(self):
        """List forms - most common operation"""
        self.client.get('/api/v1/forms', headers=self.headers)
    
    @task(2)
    def get_form(self):
        """Get specific form"""
        self.client.get('/api/v1/forms/test-form-id', headers=self.headers)
    
    @task(1)
    def submit_response(self):
        """Submit form response"""
        self.client.post(
            '/api/v1/forms/test-form-id/responses',
            headers=self.headers,
            json={'field1': 'value1'}
        )
```

**Running load tests:**

```bash
# Test with 100 users, spawning 10/sec
locust -f tests/performance/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host http://localhost:8000

# Expected results:
# - p95 response time < 500ms
# - p99 response time < 1000ms
# - Failure rate < 1%
# - RPS > 100
```

### Resource Stress Testing

**File:** `tests/performance/stress_test.sh`

```bash
#!/bin/bash

echo "=== Starting Resource Stress Tests ==="

# Test 1: CPU Stress
echo "Test 1: CPU Stress"
stress-ng --cpu 4 --timeout 60s &
STRESS_PID=$!

# Monitor API responsiveness
for i in {1..60}; do
    response_time=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:8000/health)
    echo "Response time: $response_time"
    
    if (( $(echo "$response_time > 1.0" | bc -l) )); then
        echo "FAIL: Response time exceeded 1s during CPU stress"
        exit 1
    fi
    
    sleep 1
done

wait $STRESS_PID
echo "PASS: API remained responsive under CPU stress"

# Test 2: Memory Stress
echo "Test 2: Memory Stress"
stress-ng --vm 2 --vm-bytes 1G --timeout 60s &
STRESS_PID=$!

# Check for OOM kills
sleep 60
if dmesg | grep -i "killed process" | grep -q "docker"; then
    echo "FAIL: Container was OOM killed"
    exit 1
fi

wait $STRESS_PID
echo "PASS: No OOM kills during memory stress"

# Test 3: Disk I/O Stress
echo "Test 3: Disk I/O Stress"
stress-ng --hdd 2 --timeout 60s &
STRESS_PID=$!

# Monitor database write performance
mongo_write_time=$(docker exec mongodb mongo testdb --eval \
    "db.test.insert({data: 'x'.repeat(1000)})" \
    | grep "WriteResult" | wc -l)

wait $STRESS_PID

if [ "$mongo_write_time" -lt 1 ]; then
    echo "FAIL: Database writes failed during I/O stress"
    exit 1
fi

echo "PASS: Database responsive during I/O stress"

echo "=== All Stress Tests Passed ==="
```

### Performance Benchmarking

**File:** `tests/performance/benchmark.py`

```python
import pytest
import time
from app.ai.model_loader import load_model, ModelType

class TestPerformance:
    
    @pytest.mark.benchmark(group="api")
    def test_api_response_time(self, benchmark, client):
        """Benchmark API response time"""
        result = benchmark(lambda: client.get('/api/v1/forms'))
        
        # Should be < 200ms
        assert benchmark.stats['mean'] < 0.2
    
    @pytest.mark.benchmark(group="database")
    def test_database_query_time(self, benchmark, mongo_client):
        """Benchmark database query time"""
        def query():
            return list(mongo_client.forms.find().limit(100))
        
        result = benchmark(query)
        assert benchmark.stats['mean'] < 0.1
    
    @pytest.mark.benchmark(group="ai")
    def test_ai_inference_time(self, benchmark):
        """Benchmark AI inference time"""
        model = load_model(ModelType.LLAMA_7B_Q4)
        
        def infer():
            return model.generate("Test prompt", max_tokens=50)
        
        result = benchmark(infer)
        
        # Should be < 10s for 7B model on CPU
        assert benchmark.stats['mean'] < 10.0
    
    @pytest.mark.benchmark(group="cache")
    def test_redis_latency(self, benchmark, redis_client):
        """Benchmark Redis GET/SET latency"""
        def cache_operation():
            redis_client.set('test_key', 'test_value')
            return redis_client.get('test_key')
        
        result = benchmark(cache_operation)
        
        # Should be < 5ms
        assert benchmark.stats['mean'] < 0.005
```

**Running benchmarks:**

```bash
# Run all benchmarks
pytest tests/performance/benchmark.py --benchmark-only

# Generate report
pytest tests/performance/benchmark.py \
    --benchmark-only \
    --benchmark-autosave \
    --benchmark-save-data

# Compare with baseline
pytest tests/performance/benchmark.py \
    --benchmark-only \
    --benchmark-compare=0001
```

---

## Security Testing

### Vulnerability Scanning

**File:** `tests/security/scan.sh`

```bash
#!/bin/bash

echo "=== Security Scanning ==="

# Scan Python dependencies
echo "Scanning Python dependencies..."
safety check --json > security_report_deps.json

if [ $? -ne 0 ]; then
    echo "WARNING: Vulnerable dependencies found"
    cat security_report_deps.json
fi

# Scan code with Bandit
echo "Scanning code for security issues..."
bandit -r app/ -f json -o security_report_code.json

# Scan Docker images
echo "Scanning Docker images..."
docker pull aquasec/trivy
trivy image --severity HIGH,CRITICAL \
    form-management-api:latest \
    -o security_report_image.json

# Check for exposed secrets
echo "Checking for exposed secrets..."
if grep -r "password\|secret\|api_key" --include="*.py" app/ | grep -v "# nosec"; then
    echo "FAIL: Potential secrets found in code"
    exit 1
fi

echo "=== Security Scan Complete ==="
```

### Penetration Testing

**File:** `tests/security/pentest.py`

```python
import pytest
import requests

class TestSecurityPenetration:
    
    def test_sql_injection(self, client):
        """Test SQL injection vulnerability"""
        payloads = [
            "' OR '1'='1",
            "1' UNION SELECT NULL--",
            "admin'--"
        ]
        
        for payload in payloads:
            response = client.get(f'/api/v1/forms?search={payload}')
            
            # Should not return database error
            assert response.status_code != 500
            assert 'error' not in response.json.get('message', '').lower()
    
    def test_xss_prevention(self, client):
        """Test XSS vulnerability"""
        xss_payload = '<script>alert("XSS")</script>'
        
        response = client.post('/api/v1/forms', json={
            'title': xss_payload,
            'fields': []
        })
        
        form_id = response.json['form_id']
        get_response = client.get(f'/api/v1/forms/{form_id}')
        
        # Payload should be escaped
        assert '<script>' not in str(get_response.data)
    
    def test_authentication_bypass(self, client):
        """Test authentication bypass attempts"""
        protected_endpoints = [
            '/api/v1/forms',
            '/api/v1/users/profile',
            '/api/v1/admin/stats'
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_rate_limiting(self, client):
        """Test rate limiting is enforced"""
        # Make 100 rapid requests
        responses = []
        for i in range(100):
            response = client.post('/api/v1/auth/login', json={
                'username': 'test',
                'password': 'wrong'
            })
            responses.append(response.status_code)
        
        # Should have at least one 429 (Too Many Requests)
        assert 429 in responses
    
    def test_jwt_expiration(self, client):
        """Test JWT tokens expire"""
        # Login
        response = client.post('/api/v1/auth/login', json={
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        token = response.json['token']
        
        # Manipulate token to be expired (in real test, wait or mock time)
        import jwt
        import time
        
        # This should fail in production
        expired_token = jwt.encode(
            {'user_id': 1, 'exp': time.time() - 3600},
            'wrong-secret',
            algorithm='HS256'
        )
        
        response = client.get(
            '/api/v1/forms',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        assert response.status_code == 401
```

---

## Chaos Testing

### Container Failure Tests

**File:** `tests/chaos/test_container_failures.py`

```python
import pytest
import docker
import time
import requests

@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()

def test_api_container_restart(docker_client):
    """Test system recovers from API container restart"""
    
    # Find API container
    containers = docker_client.containers.list(
        filters={'name': 'api'}
    )
    api_container = containers[0]
    
    # Verify API is working
    response = requests.get('http://localhost:8000/health')
    assert response.status_code == 200
    
    # Kill container
    api_container.kill()
    
    # Wait for restart
    time.sleep(10)
    
    # Verify API is working again
    response = requests.get('http://localhost:8000/health')
    assert response.status_code == 200

def test_database_container_restart(docker_client):
    """Test system recovers from database restart"""
    
    containers = docker_client.containers.list(
        filters={'name': 'mongodb'}
    )
    db_container = containers[0]
    
    # Create test data
    response = requests.post('http://localhost:8000/api/v1/forms', json={
        'title': 'Test Form',
        'fields': []
    })
    form_id = response.json['form_id']
    
    # Kill database
    db_container.kill()
    
    # Wait for restart
    time.sleep(15)
    
    # Verify data still exists
    response = requests.get(f'http://localhost:8000/api/v1/forms/{form_id}')
    assert response.status_code == 200
    assert response.json['title'] == 'Test Form'

def test_worker_container_kill_during_task(docker_client):
    """Test task is requeued when worker killed mid-processing"""
    
    # Queue a long-running task
    response = requests.post('http://localhost:8000/api/v1/forms/analyze', json={
        'prompt': 'Long analysis task'
    })
    task_id = response.json['task_id']
    
    # Wait a bit for task to start
    time.sleep(2)
    
    # Kill worker container
    containers = docker_client.containers.list(
        filters={'name': 'worker'}
    )
    worker_container = containers[0]
    worker_container.kill()
    
    # Wait for new worker to start
    time.sleep(10)
    
    # Verify task eventually completes
    max_wait = 60
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}')
        if response.json['status'] in ['SUCCESS', 'FAILURE']:
            break
        time.sleep(2)
    
    assert response.json['status'] == 'SUCCESS'
```

### Network Partition Tests

**File:** `tests/chaos/test_network_failures.py`

```bash
#!/bin/bash

echo "=== Network Partition Tests ==="

# Test 1: Partition API from Database
echo "Test 1: API <-> Database partition"

# Block traffic between API and MongoDB
docker network disconnect backend api-container

# API should handle gracefully
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/forms)

if [ "$response" != "503" ]; then
    echo "FAIL: Expected 503 Service Unavailable, got $response"
    docker network connect backend api-container
    exit 1
fi

# Reconnect
docker network connect backend api-container
sleep 5

# Verify recovery
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$response" != "200" ]; then
    echo "FAIL: Service did not recover"
    exit 1
fi

echo "PASS: Service handled database partition gracefully"

# Test 2: Partition Worker from Redis
echo "Test 2: Worker <-> Redis partition"

# Block worker from Redis
docker network disconnect backend worker-container

# Queue a task (should queue but not process)
task_id=$(curl -s -X POST http://localhost:8000/api/v1/test-task | jq -r '.task_id')

sleep 10

# Task should be PENDING
status=$(curl -s http://localhost:8000/api/v1/tasks/$task_id | jq -r '.status')

if [ "$status" != "PENDING" ]; then
    echo "FAIL: Expected PENDING status, got $status"
    docker network connect backend worker-container
    exit 1
fi

# Reconnect worker
docker network connect backend worker-container
sleep 10

# Task should now complete
status=$(curl -s http://localhost:8000/api/v1/tasks/$task_id | jq -r '.status')

if [ "$status" != "SUCCESS" ]; then
    echo "FAIL: Task did not complete after reconnection"
    exit 1
fi

echo "PASS: Task completed after network recovery"

echo "=== All Network Partition Tests Passed ==="
```

---

## Test Automation

### CI/CD Integration

**File:** `.github/workflows/test.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ \
          --cov=app \
          --cov-report=xml \
          --cov-report=term
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start test environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
        ./scripts/wait-for-services.sh
    
    - name: Run integration tests
      run: |
        docker-compose -f docker-compose.test.yml exec -T api \
          pytest tests/integration/
    
    - name: Collect logs
      if: failure()
      run: |
        docker-compose -f docker-compose.test.yml logs > test-logs.txt
    
    - name: Upload logs
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: test-logs
        path: test-logs.txt
    
    - name: Tear down
      if: always()
      run: docker-compose -f docker-compose.test.yml down -v

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        ./tests/security/scan.sh
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: security_report_*.json

  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start services
      run: docker-compose up -d
    
    - name: Run load tests
      run: |
        pip install locust
        locust -f tests/performance/locustfile.py \
          --headless \
          --users 50 \
          --spawn-rate 5 \
          --run-time 3m \
          --host http://localhost:8000 \
          --html performance-report.html
    
    - name: Upload performance report
      uses: actions/upload-artifact@v3
      with:
        name: performance-report
        path: performance-report.html
```

---

## Test Data Management

### Test Data Fixtures

**File:** `tests/fixtures/forms.py`

```python
import pytest
from app.models import Form, FormVersion

@pytest.fixture
def sample_form():
    """Create a sample form for testing"""
    return {
        'title': 'Test Form',
        'description': 'A form for testing',
        'fields': [
            {
                'name': 'name',
                'type': 'text',
                'label': 'Full Name',
                'required': True
            },
            {
                'name': 'email',
                'type': 'email',
                'label': 'Email Address',
                'required': True
            },
            {
                'name': 'message',
                'type': 'textarea',
                'label': 'Message',
                'required': False
            }
        ]
    }

@pytest.fixture
def complex_form():
    """Create a complex form with all field types"""
    return {
        'title': 'Complex Test Form',
        'fields': [
            {'name': 'text_field', 'type': 'text'},
            {'name': 'number_field', 'type': 'number'},
            {'name': 'email_field', 'type': 'email'},
            {'name': 'date_field', 'type': 'date'},
            {'name': 'select_field', 'type': 'select', 'options': ['A', 'B', 'C']},
            {'name': 'checkbox_field', 'type': 'checkbox'},
            {'name': 'radio_field', 'type': 'radio', 'options': ['X', 'Y', 'Z']}
        ]
    }

@pytest.fixture
def ai_enabled_form():
    """Create a form with AI features"""
    return {
        'title': 'AI-Enabled Form',
        'fields': [
            {
                'name': 'user_input',
                'type': 'textarea',
                'ai_enabled': True,
                'ai_task': 'sentiment_analysis'
            }
        ],
        'webhook_url': 'https://webhook.site/test'
    }
```

### Database Seeding

**File:** `tests/fixtures/seed_data.py`

```python
from pymongo import MongoClient
import redis
from datetime import datetime, timedelta

def seed_test_database(mongo_url, redis_url):
    """Seed test database with sample data"""
    
    # MongoDB
    client = MongoClient(mongo_url)
    db = client.test_db
    
    # Clear existing data
    db.forms.delete_many({})
    db.responses.delete_many({})
    
    # Insert forms
    forms = [
        {
            'form_id': 'form-001',
            'title': 'Contact Form',
            'created_at': datetime.utcnow() - timedelta(days=30)
        },
        {
            'form_id': 'form-002',
            'title': 'Feedback Form',
            'created_at': datetime.utcnow() - timedelta(days=15)
        }
    ]
    db.forms.insert_many(forms)
    
    # Insert responses
    responses = []
    for i in range(100):
        responses.append({
            'form_id': 'form-001',
            'response_id': f'resp-{i:03d}',
            'data': {'name': f'User {i}', 'email': f'user{i}@example.com'},
            'created_at': datetime.utcnow() - timedelta(days=i % 30)
        })
    db.responses.insert_many(responses)
    
    # Redis
    r = redis.from_url(redis_url)
    r.flushdb()
    
    # Set some cache data
    r.setex('form:form-001', 3600, '{"title": "Contact Form"}')
    
    print("Test database seeded successfully")
```

---

## Reporting

### Test Report Generation

**File:** `scripts/generate_test_report.sh`

```bash
#!/bin/bash

echo "Generating Test Report..."

# Run all tests with coverage
pytest \
  --cov=app \
  --cov-report=html:reports/coverage \
  --cov-report=term \
  --html=reports/test-report.html \
  --self-contained-html \
  --junitxml=reports/junit.xml

# Run benchmarks
pytest tests/performance/benchmark.py \
  --benchmark-only \
  --benchmark-json=reports/benchmark.json

# Generate security report
./tests/security/scan.sh

# Combine reports
python scripts/combine_reports.py

echo "Reports generated in ./reports/"
echo "  - coverage/index.html"
echo "  - test-report.html"
echo "  - benchmark.json"
echo "  - security_report.json"
```

### Metrics Tracking

**File:** `scripts/track_metrics.py`

```python
import json
from datetime import datetime

def track_test_metrics():
    """Track test metrics over time"""
    
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'test_counts': {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        },
        'coverage': {
            'line_coverage': 0.0,
            'branch_coverage': 0.0
        },
        'performance': {
            'api_p95': 0.0,
            'ai_inference_mean': 0.0
        },
        'security': {
            'vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
    }
    
    # Save metrics
    with open('reports/metrics_history.jsonl', 'a') as f:
        f.write(json.dumps(metrics) + '\n')
    
    print(f"Metrics tracked: {metrics}")
```

---

## Summary

This testing guide provides comprehensive coverage for all infrastructure components:

✅ **Unit Tests:** Individual component validation  
✅ **Integration Tests:** Service communication validation  
✅ **Performance Tests:** Load, stress, and benchmark validation  
✅ **Security Tests:** Vulnerability and penetration testing  
✅ **Chaos Tests:** Failure recovery validation  
✅ **Automation:** CI/CD integration  
✅ **Reporting:** Metrics tracking and reporting

**Expected Test Coverage:**
- Unit Tests: > 80%
- Integration Tests: All critical paths
- Performance: All NFR targets met
- Security: No high/critical vulnerabilities
- Chaos: All failure scenarios handled

---

**Next Steps:**
1. Set up test environment
2. Write and run unit tests
3. Implement integration tests
4. Execute performance tests
5. Run security scans
6. Perform chaos testing
7. Generate reports
8. Track metrics over time
