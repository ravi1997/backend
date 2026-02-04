# M4: Redis Integration & Performance - Technical Architecture

## Overview

This document outlines the technical architecture for implementing comprehensive Redis caching strategies to improve application performance and reduce database load.

## System Architecture

### Current State

```
┌─────────────────┐
│   Flask API    │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MongoDB      │
│   (Primary DB)  │
└─────────────────┘
```

### Target State

```
┌─────────────────┐
│   Flask API    │
│                 │
└────────┬────────┘
         │
         ├─────────────┐
         │             │
         ▼             ▼
┌─────────────────┐  ┌─────────────────┐
│   Redis Cache  │  │   MongoDB      │
│   (Fast Layer)  │  │   (Primary DB)  │
└─────────────────┘  └─────────────────┘
```

## Component Design

### 1. Enhanced Redis Client

**File:** `app/utils/redis_client.py` (extend existing)

```python
class EnhancedRedisClient:
    def __init__(self):
        self.redis = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        self.locks = {}  # In-memory lock registry
        
    def get_with_fallback(self, key, fallback_func, ttl=300):
        """Get from cache, fallback to DB if miss"""
        value = self.redis.get(key)
        if value is None:
            value = fallback_func()
            self.set(key, value, ttl)
        return value
    
    def invalidate_pattern(self, pattern):
        """Invalidate all keys matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def get_cache_stats(self):
        """Get comprehensive cache statistics"""
        info = self.redis.info('stats')
        return {
            'total_keys': info['keyspace_hits'],
            'hit_ratio': info.get('hit_ratio', 0),
            'memory_used': info['used_memory_human'],
            'evictions': info['evicted_keys']
        }
```

### 2. Cache Layer Service

**File:** `app/services/cache_service.py` (new)

```python
class CacheService:
    """High-level cache abstraction"""
    
    CACHE_TYPES = {
        'form_schema': {'ttl': 3600, 'max_entries': 1000},
        'user_session': {'ttl': 1800, 'max_entries': 5000},
        'query_result': {'ttl': 300, 'max_entries': 10000},
        'dashboard_widget': {'ttl': 120, 'max_entries': 5000}
    }
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    def cache_form_schema(self, form_id, schema):
        """Cache form schema with invalidation"""
        key = f"form:schema:{form_id}"
        self.redis.set(key, json.dumps(schema), ex=3600)
        
    def invalidate_form_schema(self, form_id):
        """Invalidate form schema cache"""
        key = f"form:schema:{form_id}"
        self.redis.delete(key)
        
    def cache_query_result(self, query_hash, results):
        """Cache NLP search results"""
        key = f"query:result:{query_hash}"
        self.redis.set(key, json.dumps(results), ex=300)
        
    def warmup_cache(self):
        """Pre-warm cache on startup"""
        # Cache top 100 forms
        # Cache active user sessions
        # Cache common dashboard widgets
```

### 3. Cache Middleware

**File:** `app/middleware/cache_middleware.py` (new)

```python
from functools import wraps

def cache_response(ttl=60, key_func=None):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{f.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached = cache_service.get(cache_key)
            if cached:
                return cached, 200, {'X-Cache': 'HIT'}
            
            # Execute and cache result
            result = f(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            return result, 200, {'X-Cache': 'MISS'}
        return decorated_function
    return decorator
```

### 4. Cache Invalidation Service

**File:** `app/services/cache_invalidation_service.py` (new)

```python
class CacheInvalidationService:
    """Event-driven cache invalidation"""
    
    def __init__(self, redis_client, event_bus):
        self.redis = redis_client
        self.event_bus = event_bus
        
    def on_form_updated(self, form_id):
        """Handle form update event"""
        self.redis.invalidate_pattern(f"form:schema:{form_id}")
        self.redis.invalidate_pattern(f"dashboard:widget:*:{form_id}")
        
    def on_response_submitted(self, form_id):
        """Handle form submission event"""
        self.redis.invalidate_pattern(f"dashboard:widget:*:{form_id}")
        self.redis.invalidate_pattern(f"query:result:*:{form_id}")
        
    def on_user_permission_changed(self, user_id):
        """Handle permission change event"""
        self.redis.invalidate_pattern(f"user:session:{user_id}")
        self.redis.invalidate_pattern(f"dashboard:widget:{user_id}:*")
```

## Data Flow

### Read Flow

```
1. API Request
   ↓
2. Check Cache (Redis)
   ├─ HIT → Return cached response (X-Cache: HIT)
   └─ MISS → Continue to step 3
   ↓
3. Query Database (MongoDB)
   ↓
4. Cache Result (Redis)
   ↓
5. Return Response (X-Cache: MISS)
```

### Write Flow

```
1. Write Request
   ↓
2. Write to Database (MongoDB)
   ↓
3. Invalidate Related Cache (Redis)
   ↓
4. Publish Event (Event Bus)
   ↓
5. Return Response
```

## Cache Key Strategy

### Key Naming Convention

```
form:schema:{form_id}
user:session:{user_id}
query:result:{query_hash}
dashboard:widget:{user_id}:{widget_id}
api:response:{endpoint}:{params_hash}
```

### Key Hashing

```python
import hashlib

def generate_cache_key(prefix, *args):
    """Generate consistent cache key"""
    data = ":".join(str(a) for a in args)
    hash_value = hashlib.sha256(data.encode()).hexdigest()[:16]
    return f"{prefix}:{hash_value}"
```

## Performance Optimization

### 1. Pipeline Operations

```python
def batch_cache_get(keys):
    """Get multiple keys in single round-trip"""
    pipe = redis.pipeline()
    for key in keys:
        pipe.get(key)
    return pipe.execute()
```

### 2. Compression

```python
import gzip
import pickle

def compress_cache_value(value):
    """Compress large values"""
    if len(json.dumps(value)) > 1024:
        return gzip.compress(pickle.dumps(value))
    return value

def decompress_cache_value(value):
    """Decompress cached values"""
    try:
        return pickle.loads(gzip.decompress(value))
    except:
        return value
```

### 3. Connection Pooling

```python
from redis.connection import ConnectionPool

pool = ConnectionPool(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    max_connections=50,
    retry_on_timeout=True
)
```

## Monitoring & Observability

### Metrics to Track

1. **Cache Hit Ratio**: `hits / (hits + misses)`
2. **Cache Latency**: Average get/set time
3. **Memory Usage**: Current memory consumption
4. **Eviction Rate**: Keys evicted per minute
5. **Error Rate**: Cache operation failures

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

cache_hits = Counter('cache_hits_total', 'Total cache hits')
cache_misses = Counter('cache_misses_total', 'Total cache misses')
cache_latency = Histogram('cache_latency_seconds', 'Cache operation latency')

def track_cache_operation(operation, hit, latency):
    if hit:
        cache_hits.inc()
    else:
        cache_misses.inc()
    cache_latency.observe(latency)
```

### Health Check Endpoint

```python
@app.route('/api/v1/health/cache')
def cache_health():
    stats = cache_service.get_stats()
    return {
        'status': 'healthy' if stats['hit_ratio'] > 0.7 else 'degraded',
        'hit_ratio': stats['hit_ratio'],
        'memory_used': stats['memory_used'],
        'uptime': uptime_seconds()
    }
```

## Deployment Architecture

### Development

```yaml
# docker-compose.dev.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### Production

```yaml
# docker-compose.prod.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru --appendonly yes
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## Migration Strategy

### Phase 1: Infrastructure Setup (Week 1)

1. Deploy Redis instance
2. Configure connection pooling
3. Setup monitoring

### Phase 2: Core Caching (Week 2)

1. Implement form schema caching
2. Implement user session caching
3. Add cache middleware

### Phase 3: Advanced Features (Week 3)

1. Implement query result caching
2. Implement dashboard widget caching
3. Add cache invalidation events

### Phase 4: Optimization (Week 4)

1. Add compression
2. Implement pipeline operations
3. Performance tuning

## Configuration

### Environment Variables

```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_MEMORY=256mb
REDIS_MAX_CONNECTIONS=50
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=300
```

---

**Last Updated:** 2026-02-04  
**Version:** 1.0
