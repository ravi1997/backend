# Test Strategy
# Plan 3: Advanced Analytics, Performance & Integration Ecosystem

**Version:** 1.0  
**Date:** 2026-01-09  
**Status:** Active

---

## EXECUTIVE SUMMARY

This document outlines the comprehensive testing strategy for Plan 3, ensuring that all analytics, performance optimization, integration, and reporting features meet quality standards before production deployment.

### Testing Objectives
1. **Functional Correctness:** All features work as specified in SRS
2. **Performance Targets:** Meet <100ms API response time (p95)
3. **Reliability:** 99.9% uptime and webhook delivery
4. **Security:** No vulnerabilities in plugins or integrations
5. **Scalability:** Support 1000+ concurrent users

### Test Coverage Goals
- Unit Tests: **>80% code coverage**
- Integration Tests: **All API endpoints**
- Performance Tests: **All critical paths**
- Security Tests: **All external integrations**

---

## 1. UNIT TESTING

### 1.1 Analytics Engine Tests

#### Test File: `tests/test_analytics/test_aggregator.py`

**Test Cases:**
```python
import pytest
from app.analytics.aggregator import FormAggregator
from unittest.mock import Mock
import redis

@pytest.fixture
def redis_client():
    """Mock Redis client for testing."""
    return Mock(spec=redis.Redis)

@pytest.fixture
def aggregator(redis_client):
    return FormAggregator(redis_client)

class TestFormAggregator:
    """Test suite for analytics aggregator."""
    
    def test_increment_response_count(self, aggregator, redis_client):
        """TC-AN-001: Verify response count increments correctly."""
        form_id = "test-form-123"
        
        aggregator.on_response_submitted(form_id, {"field1": "value1"})
        
        redis_client.hincrby.assert_called_with(
            f"form:{form_id}:stats",
            "total_responses",
            1
        )
    
    def test_update_field_distribution(self, aggregator, redis_client):
        """TC-AN-005: Verify field distribution tracking."""
        form_id = "test-form-123"
        response_data = {
            "department": "IT",
            "rating": 5
        }
        
        aggregator.on_response_submitted(form_id, response_data)
        
        # Verify department distribution updated
        redis_client.hincrby.assert_any_call(
            f"form:{form_id}:field:department:dist",
            "IT",
            1
        )
    
    def test_timeseries_cleanup(self, aggregator, redis_client):
        """TC-AN-008: Verify old timeseries data is removed."""
        from datetime import datetime, timedelta
        form_id = "test-form-123"
        
        # Submit response
        aggregator._update_timeseries(form_id, datetime.utcnow())
        
        # Verify old data removed (24 hours for hourly)
        assert redis_client.zremrangebyscore.called
    
    def test_get_metrics(self, aggregator, redis_client):
        """TC-AN-002: Verify metrics retrieval."""
        form_id = "test-form-123"
        
        # Mock Redis response
        redis_client.hgetall.return_value = {
            b"total_responses": b"150",
            b"completion_rate": b"0.85"
        }
        
        metrics = aggregator.get_metrics(form_id)
        
        assert metrics["total_responses"] == 150
        assert metrics["completion_rate"] == 0.85
```

#### Test File: `tests/test_analytics/test_query_builder.py`

**Test Cases:**
```python
import pytest
from app.analytics.query_builder import QueryDSL

class TestQueryDSL:
    """Test suite for query builder."""
    
    def test_parse_valid_query(self):
        """TC-AN-010: Parse valid DSL query."""
        query = {
            "aggregate": "count",
            "group_by": "data.department",
            "filter": {
                "data.status": {"$eq": "approved"}
            }
        }
        
        dsl = QueryDSL(None)
        parsed = dsl.parse(query)
        
        assert parsed["aggregate"] == "count"
        assert "filter" in parsed
    
    def test_reject_invalid_aggregation(self):
        """TC-AN-011: Reject invalid aggregation function."""
        query = {
            "aggregate": "invalid_func",  # Invalid
            "group_by": "data.department"
        }
        
        dsl = QueryDSL(None)
        
        with pytest.raises(ValueError, match="Invalid aggregation"):
            dsl.parse(query)
    
    def test_reject_disallowed_operator(self):
        """TC-AN-018: Security - reject disallowed operators."""
        query = {
            "aggregate": "count",
            "filter": {
                "data.field": {"$where": "malicious_code"}  # Injection attempt
            }
        }
        
        dsl = QueryDSL(None)
        
        with pytest.raises(ValueError, match="not allowed"):
            dsl.parse(query)
    
    def test_mongo_pipeline_generation(self):
        """TC-AN-016: Generate correct MongoDB pipeline."""
        query = {
            "aggregate": "count",
            "group_by": "data.department",
            "filter": {
                "data.status": {"$eq": "approved"}
            }
        }
        
        dsl = QueryDSL(None)
        pipeline = dsl.to_mongo_pipeline(query)
        
        assert len(pipeline) >= 2  # Match + Group
        assert pipeline[0]["$match"] is not None
        assert pipeline[1]["$group"] is not None
```

---

### 1.2 Caching Tests

#### Test File: `tests/test_caching/test_decorators.py`

**Test Cases:**
```python
import pytest
from app.caching.decorators import cached
from flask import Flask
import time

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

class TestCacheDecorator:
    """Test cached decorator functionality."""
    
    def test_cache_hit_from_l1(self, app):
        """TC-PF-007: Verify L1 cache hit."""
        call_count = 0
        
        @app.route('/test')
        @cached(ttl=300)
        def test_route():
            nonlocal call_count
            call_count += 1
            return {"data": "value"}
        
        with app.test_client() as client:
            # First call - cache miss
            response1 = client.get('/test')
            assert call_count == 1
            
            # Second call - cache hit
            response2 = client.get('/test')
            assert call_count == 1  # Not called again
            assert response1.json == response2.json
    
    def test_cache_expiration(self, app):
        """TC-PF-008: Verify cache TTL expiration."""
        call_count = 0
        
        @app.route('/test')
        @cached(ttl=1)  # 1 second TTL
        def test_route():
            nonlocal call_count
            call_count += 1
            return {"data": "value", "count": call_count}
        
        with app.test_client() as client:
            response1 = client.get('/test')
            time.sleep(2)  # Wait for expiration
            response2 = client.get('/test')
            
            assert response1.json["count"] == 1
            assert response2.json["count"] == 2  # Cache expired
    
    def test_different_params_different_cache(self, app):
        """TC-PF-009: Different query params = different cache keys."""
        calls = []
        
        @app.route('/test')
        @cached(ttl=300)
        def test_route():
            from flask import request
            param = request.args.get('param')
            calls.append(param)
            return {"param": param}
        
        with app.test_client() as client:
            client.get('/test?param=a')
            client.get('/test?param=b')
            client.get('/test?param=a')  # Should hit cache
            
            assert len(calls) == 2  # Only 'a' and 'b', not third call
```

---

### 1.3 Webhook Tests

#### Test File: `tests/test_integrations/test_webhooks.py`

**Test Cases:**
```python
import pytest
from app.integrations.webhooks.delivery import deliver_webhook, generate_hmac_signature
from unittest.mock import Mock, patch
import requests

class TestWebhookDelivery:
    """Test webhook delivery system."""
    
    @patch('requests.post')
    def test_successful_delivery(self, mock_post):
        """TC-IN-001: Webhook delivers successfully on first attempt."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"
        
        result = deliver_webhook(
            webhook_id="webhook-123",
            payload={"form_id": "form-456", "response_id": "resp-789"},
            signature_secret="secret-key"
        )
        
        assert result["status"] == "delivered"
        assert result["attempt"] == 1
        assert mock_post.called
    
    @patch('requests.post')
    def test_retry_on_failure(self, mock_post):
        """TC-IN-002: Webhook retries on failure."""
        # Simulate failure then success
        mock_post.side_effect = [
            requests.RequestException("Connection failed"),
            Mock(status_code=200, text="OK")
        ]
        
        # This test requires async execution simulation
        # In real implementation, use Celery test utilities
    
    def test_hmac_signature_generation(self):
        """TC-IN-011: HMAC signature generation."""
        payload = {"form_id": "test", "data": {"field1": "value1"}}
        secret = "test-secret"
        
        signature1 = generate_hmac_signature(payload, secret)
        signature2 = generate_hmac_signature(payload, secret)
        
        # Same payload + secret = same signature
        assert signature1 == signature2
        assert len(signature1) == 64  # SHA256 hex = 64 chars
    
    def test_hmac_signature_verification(self):
        """TC-IN-012: HMAC signature verification prevents tampering."""
        payload = {"form_id": "test"}
        secret = "test-secret"
        
        signature = generate_hmac_signature(payload, secret)
        
        # Tampered payload should have different signature
        tampered_payload = {"form_id": "test-modified"}
        tampered_signature = generate_hmac_signature(tampered_payload, secret)
        
        assert signature != tampered_signature
```

---

## 2. INTEGRATION TESTING

### 2.1 API Endpoint Tests

#### Test File: `tests/test_api/test_analytics_endpoints.py`

**Test Cases:**
```python
import pytest
from app import create_app
from app.models.FormVersion import FormVersion
from app.models.FormResponse import FormResponse

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

class TestAnalyticsAPI:
    """Integration tests for analytics API."""
    
    def test_get_form_metrics(self, client):
        """TC-AN-001: GET /api/v2/analytics/forms/{id}/metrics"""
        # Setup: Create form with responses
        form = FormVersion.create_test_form()
        for i in range(10):
            FormResponse.create_test_response(form_id=form.id)
        
        # Execute
        response = client.get(f'/api/v2/analytics/forms/{form.id}/metrics')
        
        # Assert
        assert response.status_code == 200
        data = response.json
        assert data["total_responses"] == 10
        assert "completion_rate" in data
        assert "today_submissions" in data
    
    def test_get_timeseries_data(self, client):
        """TC-AN-003: GET /api/v2/analytics/forms/{id}/timeseries"""
        form = FormVersion.create_test_form()
        
        response = client.get(
            f'/api/v2/analytics/forms/{form.id}/timeseries',
            query_string={'granularity': 'day', 'days': 30}
        )
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data["timeseries"], list)
        assert len(data["timeseries"]) <= 30
    
    def test_execute_query_dsl(self, client):
        """TC-AN-010: POST /api/v2/analytics/query"""
        form = FormVersion.create_test_form()
        
        # Create responses with different departments
        for dept in ["IT", "HR", "Finance"]:
            FormResponse.create_test_response(
                form_id=form.id,
                data={"department": dept}
            )
        
        query = {
            "form_id": str(form.id),
            "aggregate": "count",
            "group_by": "data.department"
        }
        
        response = client.post('/api/v2/analytics/query', json=query)
        
        assert response.status_code == 200
        results = response.json["results"]
        assert len(results) == 3  # 3 departments
        assert any(r["_id"] == "IT" for r in results)
    
    def test_prediction_endpoint(self, client):
        """TC-AN-025: GET /api/v2/analytics/predict/next-week"""
        form = FormVersion.create_test_form()
        
        # Need 30+ days of data for prediction
        # (Setup code omitted for brevity)
        
        response = client.get(
            f'/api/v2/analytics/forms/{form.id}/predict/next-week'
        )
        
        assert response.status_code == 200
        data = response.json
        assert "predicted_submissions" in data
        assert "confidence_interval" in data
```

---

## 3. PERFORMANCE TESTING

### 3.1 Load Testing with Locust

#### Test File: `tests/load/locustfile.py`

```python
from locust import HttpUser, task, between, events
import random
import json

class FormUser(HttpUser):
    """Simulates a user interacting with the form system."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Setup: Login and get test data."""
        # Authenticate
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get list of forms
        response = self.client.get("/api/v1/forms", headers=self.headers)
        self.form_ids = [f["id"] for f in response.json()["forms"][:10]]
    
    @task(3)
    def view_form(self):
        """TC-NFR-001: Test form retrieval performance."""
        form_id = random.choice(self.form_ids)
        with self.client.get(
            f"/api/v1/forms/{form_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 0.1:  # 100ms threshold
                response.failure(f"Too slow: {response.elapsed.total_seconds()}s")
    
    @task(2)
    def submit_response(self):
        """TC-NFR-006: Test submission throughput."""
        form_id = random.choice(self.form_ids)
        data = {
            "field1": f"value_{random.randint(1, 1000)}",
            "field2": random.choice(["A", "B", "C"])
        }
        self.client.post(
            f"/api/v1/forms/{form_id}/responses",
            json=data,
            headers=self.headers
        )
    
    @task(1)
    def view_analytics(self):
        """TC-NFR-002: Test analytics query performance."""
        form_id = random.choice(self.form_ids)
        with self.client.get(
            f"/api/v2/analytics/forms/{form_id}/metrics",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 0.5:  # 500ms threshold
                response.failure(f"Analytics too slow: {response.elapsed.total_seconds()}s")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Report final statistics."""
    stats = environment.stats
    
    print("\n===== PERFORMANCE TEST RESULTS =====")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failures: {stats.total.num_failures}")
    print(f"RPS: {stats.total.current_rps:.2f}")
    print(f"Median response time: {stats.total.median_response_time}ms")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print(f"99th percentile: {stats.total.get_response_time_percentile(0.99)}ms")
    
    # Validate against targets
    p95 = stats.total.get_response_time_percentile(0.95)
    if p95 > 100:
        print(f"❌ FAILED: p95 ({p95}ms) exceeds 100ms target")
    else:
        print(f"✅ PASSED: p95 ({p95}ms) meets <100ms target")
```

**Running Load Tests:**
```bash
# Test with 1000 concurrent users
locust -f tests/load/locustfile.py \
    --headless \
    --users 1000 \
    --spawn-rate 100 \
    --run-time 5m \
    --host http://localhost:5000

# Test specific endpoints only
locust -f tests/load/locustfile.py \
    --tags analytics \
    --users 500 \
    --spawn-rate 50
```

---

### 3.2 Benchmark Tests

#### Test File: `tests/benchmarks/test_cache_performance.py`

```python
import pytest
import time
from app.caching.l1_cache import L1Cache
from app.caching.l2_cache import L2Cache

class TestCachePerformance:
    """Benchmarktests for caching layers."""
    
    def test_l1_cache_lookup_speed(self, benchmark):
        """TC-NFR-003: L1 cache lookup < 5ms."""
        cache = L1Cache(max_size=1000)
        cache.set("test-key", {"data": "value"}, ttl=300)
        
        def lookup():
            return cache.get("test-key")
        
        result = benchmark(lookup)
        assert result is not None
        assert benchmark.stats['mean'] < 0.005  # 5ms
    
    def test_l2_cache_lookup_speed(self, benchmark):
        """TC-NFR-003: L2 cache lookup < 10ms."""
        cache = L2Cache()
        cache.set("test-key", {"data": "value"}, ttl=300)
        
        def lookup():
            return cache.get("test-key")
        
        result = benchmark(lookup)
        assert result is not None
        assert benchmark.stats['mean'] < 0.01  # 10ms
    
    def test_cache_hit_rate(self):
        """TC-NFR-008: Cache hit rate > 80%."""
        cache = L1Cache(max_size=100)
        
        # Populate cache
        for i in range(100):
            cache.set(f"key-{i}", f"value-{i}", ttl=300)
        
        hits = 0
        misses = 0
        
        # Random access pattern (80/20 rule)
        import random
        for _ in range(1000):
            key_num = random.choices(range(100), weights=[0.8]*20 + [0.2]*80)[0]
            if cache.get(f"key-{key_num}"):
                hits += 1
            else:
                misses += 1
        
        hit_rate = hits / (hits + misses)
        assert hit_rate > 0.80
```

---

## 4. SECURITY TESTING

### 4.1 Plugin Security Tests

```python
import pytest
from app.plugins.sandbox import SecurityWrapper
from app.plugins.base import FormPlugin
import time

class TestPluginSecurity:
    """Security tests for plugin system."""
    
    def test_plugin_timeout_enforcement(self):
        """TC-NFR-019: Plugins timeout after 5 seconds."""
        class SlowPlugin(FormPlugin):
            def on_response_submitted(self, response):
                time.sleep(10)  # Intentionally slow
        
        wrapper = SecurityWrapper(timeout=5)
        plugin = SlowPlugin({})
        
        with pytest.raises(TimeoutError):
            wrapper.execute_safely(
                plugin,
                "on_response_submitted",
                Mock()
            )
    
    def test_plugin_exception_isolation(self):
        """TC-NFR-020: Plugin exceptions don't crash main app."""
        class BuggyPlugin(FormPlugin):
            def on_response_submitted(self, response):
                raise Exception("Plugin error")
        
        wrapper = SecurityWrapper()
        plugin = BuggyPlugin({})
        
        # Should not raise - error should be caught
        result = wrapper.execute_safely(
            plugin,
            "on_response_submitted",
            Mock()
        )
        
        assert result is None  # Failed gracefully
```

### 4.2 Query Injection Tests

```python
class TestQuerySecurity:
    """Security tests for analytics query builder."""
    
    def test_reject_where_operator(self):
        """TC-NFR-020: Reject $where operator (code injection)."""
        query = {
            "aggregate": "count",
            "filter": {
                "$where": "this.password == 'admin'"  # Injection attempt
            }
        }
        
        dsl = QueryDSL(None)
        with pytest.raises(ValueError):
            dsl.parse(query)
    
    def test_reject_function_injection(self):
        """TC-NFR-020: Reject function() syntax."""
        query = {
            "aggregate": "count",
            "filter": {
                "field": {"$regex": ".*function().*"}
            }
        }
        
        # $regex is allowed but should be sanitized
        dsl = QueryDSL(None)
        # Implementation should escape special characters
```

---

## 5. TEST EXECUTION PLAN

### Phase 1: Unit Testing (Week 1)
- Run all unit tests daily during development
- Target: >80% code coverage
- Fix all failures before moving to integration

### Phase 2: Integration Testing (Week 2)
- Test all API endpoints
- Verify database interactions
- Test external integrations (Zapier, Google, Salesforce)

### Phase 3: Performance Testing (Week 3)
- Baseline performance measurement
- Load testing (100, 500, 1000 concurrent users)
- Identify and fix bottlenecks
- Validate performance targets met

### Phase 4: Security & Regression (Week 4)
- Security penetration testing
- Full regression test suite
- User acceptance testing (UAT)

---

## 6. CONTINUOUS INTEGRATION

### CI Pipeline Configuration

**File:** `.github/workflows/plan3-tests.yml`

```yaml
name: Plan 3 Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-plan3.txt
          pip install pytest pytest-cov
      - name: Run unit tests
        run: pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:6.0
      redis:
        image: redis:7.0
    steps:
      - uses: actions/checkout@v2
      - name: Run integration tests
        run: pytest tests/test_api/ -v
  
  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v2
      - name: Run load tests
        run: |
          pip install locust
          locust -f tests/load/locustfile.py \
            --headless \
            --users 100 \
            --spawn-rate 10 \
            --run-time 2m
```

---

## 7. SUCCESS CRITERIA

### Test Metrics

| Metric | Target | Status |
|:-------|:-------|:-------|
| Unit Test Coverage | >80% | 📋 To measure |
| Integration Test Pass Rate | 100% | 📋 To measure |
| API Response Time (p95) | <100ms | 📋 To measure |
| Load Test Pass (1000 users) | 0 errors | 📋 To measure |
| Security Vulnerabilities | 0 critical | 📋 To assess |
| Webhook Delivery Success | >99.9% | 📋 To measure |

---

## 8. DEFECT MANAGEMENT

### Severity Levels
- **Critical:** System crash, data loss, security breach
- **High:** Core functionality broken, performance < 50% of target
- **Medium:** Feature partially working, workaround available
- **Low:** Minor issue, cosmetic problem

### Bug Triage Process
1. Developer identifies issue → Creates ticket
2. QA reproduces → Assigns severity
3. Team lead prioritizes
4. Developer fixes → Creates PR
5. QA verifies → Closes ticket

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Maintained By:** QA Team Lead
