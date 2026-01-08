# Workflow: Performance Optimization

**Purpose:** General performance tuning and optimization
**When to use:** Proactive optimization or addressing performance concerns
**Prerequisites:** Baseline metrics, profiling data
**Estimated time:** Variable (1-4 hours)
**Outputs:** Optimized application, performance report

---

## Prerequisites

- [ ] Baseline performance metrics collected
- [ ] Bottlenecks identified (use `performance_profiling.md`)
- [ ] Test environment available

---

## Step 1: Database Optimization

### Add Indexes
```sql
-- Identify missing indexes
-- PostgreSQL
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

### Optimize Queries
```python
# Use select_related for foreign keys
users = User.objects.select_related('profile').all()

# Use prefetch_related for many-to-many
users = User.objects.prefetch_related('groups').all()

# Limit fields
users = User.objects.only('id', 'name').all()
```

---

## Step 2: Caching

### Add Redis Caching
```python
from redis import Redis
cache = Redis()

def get_user(user_id):
    # Check cache first
    cached = cache.get(f'user:{user_id}')
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    user = User.query.get(user_id)
    
    # Cache for 1 hour
    cache.setex(f'user:{user_id}', 3600, json.dumps(user.to_dict()))
    return user
```

### HTTP Caching
```python
from flask import make_response

@app.route('/api/data')
def get_data():
    response = make_response(jsonify(data))
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response
```

---

## Step 3: Code Optimization

### Use Generators
```python
# ❌ BAD (loads all in memory)
def get_all_users():
    return User.query.all()

# ✅ GOOD (yields one at a time)
def get_all_users():
    for user in User.query.yield_per(100):
        yield user
```

### Batch Operations
```python
# ❌ BAD (N queries)
for item in items:
    db.session.add(Item(name=item))
    db.session.commit()

# ✅ GOOD (1 query)
db.session.bulk_insert_mappings(Item, [{'name': item} for item in items])
db.session.commit()
```

---

## Step 4: Infrastructure Optimization

### Connection Pooling
```python
# SQLAlchemy
engine = create_engine(
    'postgresql://...',
    pool_size=20,
    max_overflow=0
)
```

### Gunicorn Workers
```bash
# Increase workers
gunicorn --workers 4 --threads 2 app:app
```

---

## Step 5: Verify

```bash
# Load test
ab -n 1000 -c 10 http://localhost:8000/api/endpoint

# Monitor
# - Response times
# - Error rates
# - Resource usage
```

---

## Completion Criteria

- ✅ Performance improved (measurable)
- ✅ No regressions in functionality
- ✅ Load tests pass
- ✅ Resource usage acceptable

---

## See Also

- [`../workflows/performance_profiling.md`](performance_profiling.md)
