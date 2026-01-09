# Developer Guide
# Plan 3: Advanced Analytics, Performance & Integration Ecosystem

**Version:** 1.0  
**Date:** 2026-01-09  
**Audience:** Backend developers implementing Plan 3 features

---

## TABLE OF CONTENTS
1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture Overview](#architecture-overview)
4. [Module-by-Module Guide](#module-by-module-guide)
5. [Code Standards & Best Practices](#code-standards--best-practices)
6. [Testing Guidelines](#testing-guidelines)
7. [Debugging & Troubleshooting](#debugging--troubleshooting)
8. [Deployment Guide](#deployment-guide)

---

## 1. GETTING STARTED

### Prerequisites
- Python 3.11+
- MongoDB 6.0+ with replica set configured
- Redis 7.0+ cluster (3 nodes minimum)
- Docker & Docker Compose (for local development)
- Git for version control

### Quick Start
```bash
# Clone the repository
cd /home/programmer/Desktop/form-frontend/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Plan 3 specific dependencies
pip install -r requirements-plan3.txt

# Set up environment variables
cp .env.example .env.plan3
# Edit .env.plan3 with your local configuration

# Run database migrations
python manage.py migrate --plan3

# Start Redis cluster (Docker)
docker-compose -f docker-compose.plan3.yml up -d redis-cluster

# Start Celery workers
celery -A app.celery worker --loglevel=info &
celery -A app.celery beat --loglevel=info &

# Run the development server
python manage.py runserver
```

---

## 2. DEVELOPMENT ENVIRONMENT SETUP

### Directory Structure
```
backend/
├── app/
│   ├── analytics/              # Analytics engine
│   │   ├── aggregator.py       # Real-time metrics aggregation
│   │   ├── query_builder.py    # DSL parser and executor
│   │   └── ml/                 # Predictive analytics
│   │       └── predictor.py
│   ├── caching/                # Multi-layer caching
│   │   ├── l1_cache.py         # LRU in-memory cache
│   │   ├── l2_cache.py         # Redis cache layer
│   │   ├── decorators.py       # @cached decorator
│   │   └── replica_router.py   # Read/write splitting
│   ├── integrations/           # Integration ecosystem
│   │   ├── webhooks/
│   │   │   ├── delivery.py     # Webhook delivery engine
│   │   │   ├── templates.py    # Payload templates
│   │   │   └── security.py     # HMAC signatures
│   │   ├── plugins/
│   │   │   ├── base.py         # FormPlugin base class
│   │   │   ├── loader.py       # Plugin discovery
│   │   │   └── sandbox.py      # Security wrapper
│   │   ├── zapier/             # Zapier integration
│   │   ├── google_sheets/      # Google Sheets sync
│   │   └── salesforce/         # Salesforce connector
│   ├── reporting/              # Reporting engine
│   │   ├── pdf/
│   │   │   ├── generator.py    # PDF generation
│   │   │   └── charts.py       # Chart generation
│   │   ├── scheduler/
│   │   │   └── tasks.py        # Scheduled reports
│   │   └── transformations/
│   │       └── engine.py       # ETL and calculated fields
│   ├── routes/
│   │   └── v2/
│   │       └── analytics/      # Analytics API endpoints
│   ├── models/
│   │   └── ScheduledReport.py  # Scheduled report model
│   └── tasks/                  # Celery tasks
│       ├── analytics_tasks.py
│       ├── report_tasks.py
│       └── ml_tasks.py
├── tests/
│   ├── test_analytics/
│   ├── test_caching/
│   ├── test_integrations/
│   └── test_reporting/
├── migrations/
│   └── plan3/                  # Plan 3 specific migrations
└── config/
    ├── redis.py                # Redis configuration
    ├── celery.py               # Celery configuration
    └── features.py             # Feature flags
```

### Required Dependencies

Create `requirements-plan3.txt`:
```txt
# Analytics
pandas==2.1.4
scikit-learn==1.3.2
numpy==1.26.2

# Caching
redis==5.0.1
hiredis==2.2.3

# Background Tasks
celery[redis]==5.3.4

# PDF Generation
WeasyPrint==60.1
reportlab==4.0.7
matplotlib==3.8.2

# Integrations
requests==2.31.0
PyJWT==2.8.0
google-auth==2.25.2
google-api-python-client==2.110.0
simple-salesforce==1.12.5
cryptography==41.0.7

# Testing
locust==2.18.3
pytest-celery==0.0.0

# Monitoring
prometheus-client==0.19.0
```

### Environment Variables

Add to `.env.plan3`:
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_CLUSTER_NODES=localhost:7000,localhost:7001,localhost:7002

# MongoDB Configuration
MONGO_REPLICA_SET=rs0
MONGO_READ_PREFERENCE=secondaryPreferred

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Cache Configuration
CACHE_L1_MAX_SIZE=1000
CACHE_L1_TTL=300
CACHE_L2_DEFAULT_TTL=3600

# Analytics Configuration
ANALYTICS_ENABLE_ML=true
ML_MODEL_STORAGE_PATH=/var/models/plan3

# Webhook Configuration
WEBHOOK_MAX_RETRIES=6
WEBHOOK_TIMEOUT=10

# Plugin Configuration
PLUGIN_DIRECTORY=app/plugins
PLUGIN_ENABLE_SANDBOXING=true

# Reporting Configuration
REPORT_STORAGE_PATH=/var/reports
REPORT_MAX_FILE_SIZE=10485760  # 10MB

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_WEBHOOKS_V2=true
ENABLE_PLUGINS=true
ENABLE_PDF_REPORTS=true

# External Services
SENDGRID_API_KEY=your_sendgrid_key
AWS_S3_BUCKET=your_bucket_name
GOOGLE_OAUTH_CLIENT_ID=your_client_id
SALESFORCE_CONSUMER_KEY=your_consumer_key
```

---

## 3. ARCHITECTURE OVERVIEW

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                   │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
   ┌─────────▼─────────┐          ┌──────────▼──────────┐
   │   API Server 1    │          │   API Server 2-N    │
   │  ┌─────────────┐  │          │                     │
   │  │ L1 Cache    │  │          │   (Horizontally     │
   │  │ (LRU)       │  │          │    Scalable)        │
   │  └──────┬──────┘  │          │                     │
   └─────────┼─────────┘          └─────────────────────┘
             │
   ┌─────────▼─────────┐
   │   L2 Cache        │
   │   (Redis Cluster) │
   │   ┌──┬──┬──┐      │
   │   │N1│N2│N3│      │
   │   └──┴──┴──┘      │
   └─────────┬─────────┘
             │
   ┌─────────▼──────────────────────────────────────┐
   │        L3 (MongoDB Replica Set)                │
   │  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
   │  │ Primary  │  │Secondary1│  │Secondary2│     │
   │  │ (Write)  │  │  (Read)  │  │  (Read)  │     │
   │  └──────────┘  └──────────┘  └──────────┘     │
   └────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │          Background Workers (Celery)            │
   │  ┌──────────────┐  ┌───────────────┐           │
   │  │ Analytics    │  │  Webhooks     │           │
   │  │ Aggregation  │  │  Delivery     │           │
   │  └──────────────┘  └───────────────┘           │
   │  ┌──────────────┐  ┌───────────────┐           │
   │  │ ML Training  │  │  PDF Reports  │           │
   │  └──────────────┘  └───────────────┘           │
   └─────────────────────────────────────────────────┘
```

### Data Flow

#### 1. Request Flow (API Call)
```
User Request
    ↓
Load Balancer
    ↓
API Server
    ↓
L1 Cache (check) ─── Hit → Return response
    ↓ Miss
L2 Cache (check) ─── Hit → Store in L1 → Return
    ↓ Miss
L3 Database (query) → Store in L2 → Store in L1 → Return
```

#### 2. Analytics Flow
```
Form Submission
    ↓
Event Trigger
    ↓
Analytics Aggregator (Celery Task)
    ↓
Update Redis Metrics
    ├─ Increment counters
    ├─ Update time-series data
    └─ Calculate field distributions
    ↓
Metrics available in real-time
```

#### 3. Webhook Flow
```
Form Submission
    ↓
Webhook Trigger
    ↓
Celery Task (deliver_webhook)
    ├─ Render payload template
    ├─ Generate HMAC signature
    ├─ HTTP POST to endpoint
    └─ Handle response
        ├─ Success → Log attempt
        └─ Failure → Retry with backoff
                    ├─ Retry N times
                    └─ Move to DLQ if exhausted
```

---

## 4. MODULE-BY-MODULE GUIDE

### 4.1 Analytics Engine

#### Real-Time Metrics Aggregator

**File:** `app/analytics/aggregator.py`

```python
import redis
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

class FormAggregator:
    """
    Manages real-time aggregation of form metrics in Redis.
    
    Data Structures:
    - form:{form_id}:stats (Hash): Basic stats (total_responses, completion_rate)
    - form:{form_id}:timeseries:{granularity} (Sorted Set): Time-series data
    - form:{form_id}:field:{field_name}:dist (Hash): Field value distribution
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def on_response_submitted(self, form_id: str, response_data: dict):
        """
        Called when a new response is submitted.
        Updates all relevant metrics.
        """
        # Increment total response count
        self.redis.hincrby(f"form:{form_id}:stats", "total_responses", 1)
        
        # Update today's submission count
        today = datetime.utcnow().date().isoformat()
        self.redis.hincrby(f"form:{form_id}:stats", f"submissions:{today}", 1)
        
        # Update time-series data
        self._update_timeseries(form_id, datetime.utcnow())
        
        # Update field distributions
        for field_name, value in response_data.items():
            self._update_field_distribution(form_id, field_name, value)
    
    def _update_timeseries(self, form_id: str, timestamp: datetime):
        """Update hourly, daily, and monthly time-series data."""
        score = timestamp.timestamp()
        
        # Hourly (keep last 24 hours)
        hour_key = f"form:{form_id}:timeseries:hour"
        self.redis.zadd(hour_key, {timestamp.isoformat(): score})
        cutoff = (timestamp - timedelta(hours=24)).timestamp()
        self.redis.zremrangebyscore(hour_key, 0, cutoff)
        
        # Daily (keep last 30 days)
        day_key = f"form:{form_id}:timeseries:day"
        day_timestamp = timestamp.replace(hour=0, minute=0, second=0)
        self.redis.zincrby(day_key, 1, day_timestamp.isoformat())
        cutoff = (timestamp - timedelta(days=30)).timestamp()
        self.redis.zremrangebyscore(day_key, 0, cutoff)
        
        # Monthly (keep last 12 months)
        month_key = f"form:{form_id}:timeseries:month"
        month_timestamp = timestamp.replace(day=1, hour=0, minute=0, second=0)
        self.redis.zincrby(month_key, 1, month_timestamp.isoformat())
        cutoff = (timestamp - timedelta(days=365)).timestamp()
        self.redis.zremrangebyscore(month_key, 0, cutoff)
    
    def _update_field_distribution(self, form_id: str, field_name: str, value: Any):
        """Track value distribution for a field."""
        if value is None:
            return
        
        # Convert complex types to string
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, sort_keys=True)
        else:
            value_str = str(value)
        
        key = f"form:{form_id}:field:{field_name}:dist"
        self.redis.hincrby(key, value_str, 1)
    
    def get_metrics(self, form_id: str) -> Dict[str, Any]:
        """Retrieve all metrics for a form."""
        stats = self.redis.hgetall(f"form:{form_id}:stats")
        
        return {
            "total_responses": int(stats.get(b"total_responses", 0)),
            "today_submissions": int(stats.get(
                f"submissions:{datetime.utcnow().date().isoformat()}".encode(), 0
            )),
            "completion_rate": float(stats.get(b"completion_rate", 0.0)),
        }
    
    def get_timeseries(self, form_id: str, granularity: str = "day") -> List[Dict]:
        """Get time-series data for a specific granularity."""
        key = f"form:{form_id}:timeseries:{granularity}"
        data = self.redis.zrange(key, 0, -1, withscores=True)
        
        return [
            {"timestamp": ts.decode(), "count": int(score)}
            for ts, score in data
        ]
    
    def get_field_distribution(self, form_id: str, field_name: str) -> Dict[str, int]:
        """Get value distribution for a specific field."""
        key = f"form:{form_id}:field:{field_name}:dist"
        dist = self.redis.hgetall(key)
        
        return {k.decode(): int(v) for k, v in dist.items()}
```

**Usage Example:**
```python
# In form submission handler
from app.analytics.aggregator import FormAggregator

aggregator = FormAggregator(redis_client)
aggregator.on_response_submitted(form_id="abc123", response_data={
    "email": "user@example.com",
    "department": "IT",
    "rating": 5
})

# In analytics endpoint
metrics = aggregator.get_metrics("abc123")
timeseries = aggregator.get_timeseries("abc123", granularity="day")
```

---

#### Query Builder (DSL Parser)

**File:** `app/analytics/query_builder.py`

```python
from typing import Dict, Any, List
from pymongo import ASCENDING, DESCENDING
import re

class QueryDSL:
    """
    Parses and executes analytical queries using a custom DSL.
    
    Example Query:
    {
        "aggregate": "count",
        "group_by": "data.department",
        "filter": {
            "submitted_at": {"$gte": "2026-01-01"},
            "data.status": {"$eq": "approved"}
        }
    }
    """
    
    # Allowed operators for security
    ALLOWED_OPERATORS = {
        "$eq", "$ne", "$gt", "$lt", "$gte", "$lte", "$in", "$nin"
    }
    
    ALLOWED_AGGREGATIONS = {
        "count", "sum", "avg", "min", "max"
    }
    
    def __init__(self, form_version):
        self.form_version = form_version
    
    def parse(self, query_json: Dict) -> Dict:
        """Parse and validate the DSL query."""
        # Validate structure
        if "aggregate" not in query_json:
            raise ValueError("Query must include 'aggregate' field")
        
        if query_json["aggregate"] not in self.ALLOWED_AGGREGATIONS:
            raise ValueError(f"Invalid aggregation: {query_json['aggregate']}")
        
        # Validate filter operators
        if "filter" in query_json:
            self._validate_filter(query_json["filter"])
        
        return query_json
    
    def _validate_filter(self, filter_dict: Dict):
        """Recursively validate filter conditions."""
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                # Check operators
                for op in value.keys():
                    if op not in self.ALLOWED_OPERATORS:
                        raise ValueError(f"Operator {op} not allowed")
            elif isinstance(value, dict):
                self._validate_filter(value)
    
    def to_mongo_pipeline(self, query_json: Dict) -> List[Dict]:
        """
        Translate DSL query to MongoDB aggregation pipeline.
        """
        pipeline = []
        
        # 1. Match stage (filter)
        if "filter" in query_json:
            match_stage = {"$match": self._build_match_conditions(query_json["filter"])}
            pipeline.append(match_stage)
        
        # 2. Group stage
        group_stage = self._build_group_stage(query_json)
        pipeline.append(group_stage)
        
        # 3. Sort stage (optional)
        if "sort" in query_json:
            sort_stage = {"$sort": {
                query_json["sort"]["field"]: DESCENDING if query_json["sort"].get("desc") else ASCENDING
            }}
            pipeline.append(sort_stage)
        
        # 4. Limit stage (prevent huge result sets)
        pipeline.append({"$limit": query_json.get("limit", 1000)})
        
        return pipeline
    
    def _build_match_conditions(self, filter_dict: Dict) -> Dict:
        """Build MongoDB match conditions from filter DSL."""
        conditions = {}
        
        for field, condition in filter_dict.items():
            # Map form field names to database fields
            db_field = self._map_field_name(field)
            
            if isinstance(condition, dict):
                # Operator-based condition
                conditions[db_field] = condition
            else:
                # Direct equality
                conditions[db_field] = condition
        
        return conditions
    
    def _map_field_name(self, field: str) -> str:
        """Map DSL field names to database field names."""
        if field.startswith("data."):
            return f"data.{field[5:]}"  # Form field data
        elif field == "submitted_at":
            return "submitted_at"
        else:
            # Validate against form schema
            if not self._is_valid_field(field):
                raise ValueError(f"Invalid field name: {field}")
            return f"data.{field}"
    
    def _is_valid_field(self, field: str) -> bool:
        """Check if field exists in form schema."""
        # Implementation depends on form schema structure
        return True  # Simplified for example
    
    def _build_group_stage(self, query_json: Dict) -> Dict:
        """Build MongoDB group stage."""
        aggregate = query_json["aggregate"]
        group_by = query_json.get("group_by")
        
        if group_by:
            # Group by field
            group_stage = {
                "$group": {
                    "_id": f"${self._map_field_name(group_by)}",
                    "value": self._get_accumulator(aggregate)
                }
            }
        else:
            # Overall aggregation
            group_stage = {
                "$group": {
                    "_id": None,
                    "value": self._get_accumulator(aggregate)
                }
            }
        
        return group_stage
    
    def _get_accumulator(self, aggregate: str) -> Dict:
        """Get MongoDB accumulator expression."""
        if aggregate == "count":
            return {"$sum": 1}
        elif aggregate == "sum":
            return {"$sum": "$value"}  # Requires 'value' field in query
        elif aggregate == "avg":
            return {"$avg": "$value"}
        elif aggregate == "min":
            return {"$min": "$value"}
        elif aggregate == "max":
            return {"$max": "$value"}
        else:
            raise ValueError(f"Unknown aggregation: {aggregate}")

# Usage
from app.models.FormResponse import FormResponse

def execute_analytics_query(form_id: str, query_dsl: dict) -> dict:
    form_version = FormVersion.objects.get(id=form_id)
    builder = QueryDSL(form_version)
    
    # Parse and validate
    parsed_query = builder.parse(query_dsl)
    
    # Convert to MongoDB pipeline
    pipeline = builder.to_mongo_pipeline(parsed_query)
    
    # Execute
    results = FormResponse.objects(form=form_id).aggregate(pipeline)
    
    return list(results)
```

**Testing:**
```python
# tests/test_analytics/test_query_builder.py
def test_count_by_department():
    query = {
        "aggregate": "count",
        "group_by": "data.department",
        "filter": {
            "data.status": {"$eq": "approved"}
        }
    }
    
    results = execute_analytics_query(form_id="test-form", query_dsl=query)
    assert len(results) > 0
    assert "IT" in [r["_id"] for r in results]
```

---

### 4.2 Caching Layer

#### Cache Decorator

**File:** `app/caching/decorators.py`

```python
import functools
import hashlib
import json
from typing import Callable, Any
from flask import request
from app.caching.l1_cache import L1Cache
from app.caching.l2_cache import L2Cache

l1_cache = L1Cache(max_size=1000)
l2_cache = L2Cache()

def cached(ttl: int = 3600, key_prefix: str = None):
    """
    Multi-layer cache decorator for Flask routes.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Optional cache key prefix
    
    Usage:
        @app.route('/api/v2/analytics/metrics')
        @cached(ttl=300)
        def get_metrics():
            # Expensive operation
            return {"data": ...}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from request
            cache_key = _generate_cache_key(func, request, key_prefix)
            
            # L1 Cache check
            result = l1_cache.get(cache_key)
            if result is not None:
                return result
            
            # L2 Cache check
            result = l2_cache.get(cache_key)
            if result is not None:
                # Populate L1
                l1_cache.set(cache_key, result, ttl=min(ttl, 300))
                return result
            
            # Cache miss - execute function
            result = func(*args, **kwargs)
            
            # Store in both caches
            l2_cache.set(cache_key, result, ttl=ttl)
            l1_cache.set(cache_key, result, ttl=min(ttl, 300))
            
            return result
        
        return wrapper
    return decorator

def _generate_cache_key(func: Callable, request, prefix: str = None) -> str:
    """Generate unique cache key from request."""
    key_parts = [
        prefix or func.__name__,
        request.path,
        request.method,
    ]
    
    # Include query params
    if request.args:
        query_str = json.dumps(dict(request.args), sort_keys=True)
        key_parts.append(query_str)
    
    # Include user context (if authenticated)
    if hasattr(request, 'user') and request.user:
        key_parts.append(str(request.user.id))
    
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern."""
    l2_cache.delete_pattern(pattern)
    # L1 cache will auto-expire
```

---

### 4.3 Webhook System

#### Enhanced Webhook Delivery

**File:** `app/integrations/webhooks/delivery.py`

```python
import requests
import hmac
import hashlib
import json
from celery import Task
from app import celery
from app.models.WebhookAttempt import WebhookAttempt
from app.integrations.webhooks.templates import render_payload
from datetime import datetime

class WebhookDeliveryTask(Task):
    """Custom Celery task with retry logic."""
    
    autoretry_for = (requests.RequestException,)
    retry_kwargs = {'max_retries': 6}
    retry_backoff = True
    retry_backoff_max = 1800  # 30 minutes
    retry_jitter = True

@celery.task(bind=True, base=WebhookDeliveryTask)
def deliver_webhook(self, webhook_id: str, payload: dict, signature_secret: str):
    """
    Deliver webhook with retry logic and logging.
    
    Retry schedule:
    1. Immediate
    2. +1 second
    3. +5 seconds
    4. +30 seconds
    5. +5 minutes
    6. +30 minutes
    7. Dead-letter queue
    """
    from app.models.Webhook import Webhook
    
    webhook = Webhook.objects.get(id=webhook_id)
    
    # Render payload template
    rendered_payload = render_payload(webhook.payload_template, payload)
    
    # Generate HMAC signature
    signature = generate_hmac_signature(rendered_payload, signature_secret)
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-ID": webhook_id,
        "X-Webhook-Attempt": str(self.request.retries + 1),
    }
    
    # Create attempt record
    attempt = WebhookAttempt(
        webhook=webhook,
        attempt_number=self.request.retries + 1,
        payload=rendered_payload,
        started_at=datetime.utcnow()
    )
    
    try:
        # Send webhook
        response = requests.post(
            webhook.url,
            json=rendered_payload,
            headers=headers,
            timeout=10
        )
        
        # Log attempt
        attempt.status_code = response.status_code
        attempt.response_body = response.text[:1000]  # Truncate
        attempt.succeeded = 200 <= response.status_code < 300
        attempt.completed_at = datetime.utcnow()
        attempt.save()
        
        if not attempt.succeeded:
            raise requests.HTTPError(f"HTTP {response.status_code}")
        
        return {"status": "delivered", "attempt": self.request.retries + 1}
    
    except requests.RequestException as exc:
        # Log failed attempt
        attempt.succeeded = False
        attempt.error_message = str(exc)
        attempt.completed_at = datetime.utcnow()
        attempt.save()
        
        # Check if we've exhausted retries
        if self.request.retries >= 5:
            # Move to dead-letter queue
            move_to_dlq(webhook_id, payload, str(exc))
            return {"status": "failed", "moved_to_dlq": True}
        
        # Retry with custom backoff
        backoff_seconds = [1, 5, 30, 300, 1800][self.request.retries]
        raise self.retry(exc=exc, countdown=backoff_seconds)

def generate_hmac_signature(payload: dict, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload."""
    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return signature

def move_to_dlq(webhook_id: str, payload: dict, error: str):
    """Move failed webhook to dead-letter queue."""
    from app.models.WebhookDLQ import WebhookDLQ
    
    dlq_entry = WebhookDLQ(
        webhook_id=webhook_id,
        payload=payload,
        error_message=error,
        created_at=datetime.utcnow()
    )
    dlq_entry.save()
    
    # Send alert to admins
    from app.utils.alerts import send_webhook_failure_alert
    send_webhook_failure_alert(webhook_id, error)
```

---

## 5. CODE STANDARDS & BEST PRACTICES

### Coding Conventions
1. **Follow PEP 8** for Python code style
2. **Type Hints:** Use type hints for all function signatures
3. **Docstrings:** Use Google-style docstrings
4. **Error Handling:** Always use specific exception types
5. **Logging:** Use structured logging with context

### Example of Well-Formatted Code:
```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def process_analytics_query(
    form_id: str,
    query_dsl: Dict,
    use_cache: bool = True
) -> Optional[List[Dict]]:
    """
    Process an analytics query for a form.
    
    Args:
        form_id: Unique form identifier
        query_dsl: Query definition in DSL format
        use_cache: Whether to use cached results
    
    Returns:
        List of query results, or None if query fails
    
    Raises:
        ValueError: If query_dsl is invalid
        DatabaseError: If database query fails
    
    Example:
        >>> query = {"aggregate": "count", "group_by": "data.status"}
        >>> results = process_analytics_query("form123", query)
        >>> len(results)
        3
    """
    logger.info(
        "Processing analytics query",
        extra={"form_id": form_id, "query": query_dsl}
    )
    
    try:
        # Implementation...
        pass
    except ValueError as e:
        logger.error(
            "Invalid query DSL",
            extra={"form_id": form_id, "error": str(e)}
        )
        raise
    except Exception as e:
        logger.exception(
            "Unexpected error processing query",
            extra={"form_id": form_id}
        )
        return None
```

---

## 6. TESTING GUIDELINES

### Test Structure
```
tests/
├── test_analytics/
│   ├── test_aggregator.py
│   ├── test_query_builder.py
│   └── test_ml_predictor.py
├── test_caching/
│   ├── test_l1_cache.py
│   ├── test_l2_cache.py
│   └── test_decorators.py
├── test_integrations/
│   ├── test_webhooks.py
│   ├── test_plugins.py
│   └── test_zapier.py
└── test_reporting/
    ├── test_pdf_generator.py
    └── test_scheduled_reports.py
```

### Running Tests
```bash
# Run all Plan 3 tests
pytest tests/ -v

# Run specific module
pytest tests/test_analytics/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run load tests
locust -f tests/load/locustfile.py --headless -u 1000 -r 100
```

---

## 7. DEBUGGING & TROUBLESHOOTING

### Common Issues

#### Issue 1: Cache Misses
**Symptoms:** Slow API responses despite caching  
**Diagnosis:**
```bash
# Check Redis hit rate
redis-cli INFO stats | grep keyspace_hits
```
**Solution:** Adjust cache TTL, warm cache on startup

#### Issue 2: Celery Tasks Not Executing
**Symptoms:** Webhooks not being delivered  
**Diagnosis:**
```bash
# Check Celery workers
celery -A app.celery inspect active
celery -A app.celery inspect stats
```
**Solution:** Restart workers, check broker connection

---

## 8. DEPLOYMENT GUIDE

See `checks/deployment_checklist.md` for full deployment procedure.

**Quick deployment:**
```bash
# Build and deploy
docker build -t form-backend:plan3 .
docker push form-backend:plan3

# Run migrations
kubectl exec -it <pod> -- python manage.py migrate --plan3

# Deploy to production
kubectl apply -f k8s/plan3-deployment.yml

# Monitor rollout
kubectl rollout status deployment/form-backend-plan3
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Maintained By:** Development Team
