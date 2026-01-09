# Analytics Flow Diagram
# Plan 3: Advanced Analytics, Performance & Integration Ecosystem

**Version:** 1.0  
**Date:** 2026-01-09

---

## OVERVIEW

This document illustrates the data flow for the analytics pipeline, from form submission to real-time dashboard updates.

---

## 1. FORM SUBMISSION TO ANALYTICS PIPELINE

### High-Level Flow

```
┌─────────────────┐
│  User Submits   │
│  Form Response  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    API Server (POST /responses)         │
│  ┌──────────────────────────────────┐   │
│  │ 1. Validate submission           │   │
│  │ 2. Save to MongoDB               │   │
│  │ 3. Publish event to Redis        │   │
│  └──────────────┬───────────────────┘   │
└─────────────────┼───────────────────────┘
                  │
                  ├──────────────────────────────────┐
                  │                                  │
                  ▼                                  ▼
    ┌─────────────────────────┐        ┌──────────────────────┐
    │  Analytics Aggregator   │        │  Webhook Delivery    │
    │  (Celery Task)          │        │  (Celery Task)       │
    └──────────┬──────────────┘        └──────────────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │  Update Redis Metrics   │
    │  ┌──────────────────┐   │
    │  │ • Counters       │   │
    │  │ • Time-series    │   │
    │  │ • Distributions  │   │
    │  └──────────────────┘   │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │  Real-time Dashboard    │
    │  (Cached in Redis)      │
    └─────────────────────────┘
```

---

## 2. DETAILED ANALYTICS AGGREGATION FLOW

###Step-by-Step Process

```
Form Response Submitted
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 1: Event Published to Redis Pub/Sub                │
│                                                          │
│   Channel: "form:events"                                │
│   Message: {                                             │
│     "event": "response.submitted",                       │
│     "form_id": "abc123",                                 │
│     "response_id": "xyz789",                             │
│     "timestamp": "2026-01-09T12:00:00Z"                  │
│   }                                                      │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 2: Aggregator Task Triggered (Celery)              │
│                                                          │
│   def on_response_submitted(form_id, response_data):    │
│       aggregator = FormAggregator(redis_client)          │
│       aggregator.update_all_metrics(form_id, data)       │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ├────────────────────┬───────────────────┬─────────────────┐
                       │                    │                   │                 │
                       ▼                    ▼                   ▼                 ▼
        ┌──────────────────────┐  ┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
        │ Update Counters      │  │ Update Timeseries│  │ Update Field   │  │ Update Completion│
        │                      │  │                  │  │ Distributions  │  │ Rate             │
        │ form:{id}:stats      │  │ form:{id}:ts:hour│  │ form:{id}:     │  │                  │
        │   total_responses++  │  │ form:{id}:ts:day │  │   field:{f}:   │  │ Calc: completed/ │
        │   today_count++      │  │ form:{id}:ts:mon │  │   dist         │  │ total * 100      │
        └──────────────────────┘  └──────────────────┘  └────────────────┘  └──────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 3: Metrics Available for Query                     │
│                                                          │
│  Cache TTL: 5 minutes                                    │
│  Data Freshness: Real-time (< 1 second delay)            │
└──────────────────────────────────────────────────────────┘
```

---

## 3. ANALYTICS QUERY EXECUTION FLOW

### User Requests Analytics Data

```
User: GET /api/v2/analytics/forms/abc123/metrics
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ API Route Handler                                   │
│                                                     │
│   @cached(ttl=300)  ← L2 Cache (Redis)              │
│   def get_form_metrics(form_id):                    │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Check L1 Cache       │ ← LRU In-Memory Cache
    │ (In-Process)         │
    └──────┬───────────────┘
           │
     ┌─────┴─────┐
     │ Hit?      │
     └─────┬─────┘
       Yes │     No
           │     │
           │     ▼
           │  ┌──────────────────────┐
           │  │ Check L2 Cache       │ ← Redis
           │  │ (Shared Across API)  │
           │  └──────┬───────────────┘
           │         │
           │   ┌─────┴─────┐
           │   │ Hit?      │
           │   └─────┬─────┘
           │     Yes │     No
           │         │     │
           │         │     ▼
           │         │  ┌──────────────────────┐
           │         │  │ Query Redis Directly │
           │         │  │ (Aggregated Metrics) │
           │         │  └──────┬───────────────┘
           │         │         │
           │         └─────────┤
           │                   │
           └───────────────────┤
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Format Response JSON │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Store in L1 & L2     │
                    │ (for future requests)│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Return to User       │
                    │ Response Time: <50ms │
                    └──────────────────────┘
```

---

## 4. ADVANCED QUERY (DSL) EXECUTION FLOW

### Complex Analytical Query

```
User: POST /api/v2/analytics/query
Body: {
  "form_id": "abc123",
  "aggregate": "count",
  "group_by": "data.department",
  "filter": {
    "submitted_at": {"$gte": "2026-01-01"},
    "data.status": {"$eq": "approved"}
  }
}
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 1: Parse & Validate DSL                            │
│                                                          │
│   query_builder = QueryDSL(form_version)                 │
│   parsed_query = query_builder.parse(query_json)         │
│   ✓ Validate aggregation function                        │
│   ✓ Validate operators (prevent injection)               │
│   ✓ Validate field names against schema                  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 2: Check Query Cache                               │
│                                                          │
│   query_hash = hash(query_json)                          │
│   cached_result = redis.get(f"query:{query_hash}")       │
│                                                          │
│   If cached: return immediately                          │
└──────────────────────┬───────────────────────────────────┘
                       │ Cache Miss
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 3: Translate to MongoDB Aggregation Pipeline       │
│                                                          │
│   pipeline = query_builder.to_mongo_pipeline(query)      │
│                                                          │
│   Generated Pipeline:                                    │
│   [                                                      │
│     {                                                    │
│       "$match": {                                        │
│         "form": "abc123",                                │
│         "submitted_at": {"$gte": "2026-01-01"},          │
│         "data.status": "approved"                        │
│       }                                                  │
│     },                                                   │
│     {                                                    │
│       "$group": {                                        │
│         "_id": "$data.department",                       │
│         "count": {"$sum": 1}                             │
│       }                                                  │
│     },                                                   │
│     {"$sort": {"count": -1}},                            │
│     {"$limit": 1000}                                     │
│   ]                                                      │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 4: Execute on MongoDB                              │
│                                                          │
│   Route to Read Replica (if available)                   │
│   results = FormResponse.aggregate(pipeline)             │
│                                                          │
│   Result:                                                │
│   [                                                      │
│     {"_id": "IT", "count": 450},                         │
│     {"_id": "HR", "count": 320},                         │
│     {"_id": "Finance", "count": 180}                     │
│   ]                                                      │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 5: Cache Result & Return                           │
│                                                          │
│   redis.set(                                             │
│     f"query:{query_hash}",                               │
│     json.dumps(results),                                 │
│     ttl=3600  # 1 hour                                   │
│   )                                                      │
│                                                          │
│ Return to user                                           │
│ Response Time: <500ms                                    │
└──────────────────────────────────────────────────────────┘
```

---

## 5. PREDICTIVE ANALYTICS FLOW

### Weekly Model Training & Prediction

```
┌──────────────────────────────────────────────────────────┐
│ Celery Beat Scheduler (Weekly - Sunday 2 AM)            │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Historical Data                           │
│                                                          │
│   FOR each active form:                                  │
│     submissions = FormResponse.objects(                  │
│       form=form_id,                                      │
│       submitted_at__gte=90_days_ago                      │
│     ).only('submitted_at')                               │
│                                                          │
│   Group by date:                                         │
│   {                                                      │
│     "2025-10-10": 45,                                    │
│     "2025-10-11": 52,                                    │
│     ...                                                  │
│     "2026-01-08": 48                                     │
│   }                                                      │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 2: Preprocess Data                                 │
│                                                          │
│   import pandas as pd                                    │
│   df = pd.DataFrame({                                    │
│     'date': dates,                                       │
│     'submissions': counts                                │
│   })                                                     │
│                                                          │
│   # Feature engineering                                  │
│   df['day_of_week'] = df['date'].dt.dayofweek            │
│   df['day_of_month'] = df['date'].dt.day                 │
│   df['week_of_year'] = df['date'].dt.isocalendar().week  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 3: Train Model                                     │
│                                                          │
│   from sklearn.linear_model import LinearRegression      │
│                                                          │
│   X = df[['day_of_week', 'day_of_month', 'week_of_year']]│
│   y = df['submissions']                                  │
│                                                          │
│   model = LinearRegression()                             │
│   model.fit(X, y)                                        │
│                                                          │
│   # Evaluate                                             │
│   score = model.score(X, y)  # R² score                  │
│   mae = mean_absolute_error(y, model.predict(X))         │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 4: Store Model                                     │
│                                                          │
│   import pickle                                          │
│   model_path = f"/models/{form_id}_v{version}.pkl"       │
│   pickle.dump(model, open(model_path, 'wb'))             │
│                                                          │
│   # Store metadata                                       │
│   redis.hset(f"ml:model:{form_id}", {                    │
│     "version": version,                                  │
│     "trained_at": datetime.now(),                        │
│     "r2_score": score,                                   │
│     "mae": mae,                                          │
│     "model_path": model_path                             │
│   })                                                     │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ Model Ready for Predictions                              │
└──────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────┐
│ User: GET /api/v2/analytics/predict/next-week           │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 5: Load Model & Predict                            │
│                                                          │
│   model_metadata = redis.hgetall(f"ml:model:{form_id}")  │
│   model = pickle.load(open(model_metadata["path"]))      │
│                                                          │
│   # Prepare features for next 7 days                     │
│   next_week_features = generate_features(next_7_days)    │
│                                                          │
│   # Predict                                              │
│   predictions = model.predict(next_week_features)        │
│   total_predicted = sum(predictions)                     │
│                                                          │
│   # Calculate confidence interval (±20%)                 │
│   confidence = {                                         │
│     "lower": int(total_predicted * 0.8),                 │
│     "upper": int(total_predicted * 1.2)                  │
│   }                                                      │
│                                                          │
│   return {                                               │
│     "predicted_submissions": int(total_predicted),       │
│     "confidence_interval": confidence,                   │
│     "based_on_data": "last_90_days",                     │
│     "model_accuracy": f"R²={model_metadata['r2_score']}" │
│   }                                                      │
└──────────────────────────────────────────────────────────┘
```

---

## 6. DATA RETENTION & CLEANUP

### Automatic Data Expiration

```
┌──────────────────────────────────────────┐
│ Daily Cleanup Task (Celery Beat: 3 AM)  │
└──────────────────┬───────────────────────┘
                   │
                   ├───────────────────────────┬──────────────────────┐
                   │                           │                      │
                   ▼                           ▼                      ▼
    ┌──────────────────────┐    ┌──────────────────────┐  ┌─────────────────────┐
    │ Timeseries Cleanup   │    │ Query Cache Cleanup  │  │ ML Model Cleanup    │
    │                      │    │                      │  │                     │
    │ Remove entries       │    │ Remove cached        │  │ Delete old models   │
    │ older than:          │    │ queries older        │  │ older than 30 days  │
    │ • Hour: 24h          │    │ than 24 hours        │  │ Keep last 3         │
    │ • Day: 30d           │    │                      │  │ versions            │
    │ • Month: 12m         │    │                      │  │                     │
    └──────────────────────┘    └──────────────────────┘  └─────────────────────┘
```

---

## 7. PERFORMANCE METRICS

### Expected Performance

```
Metric                    | Target      | Measurement Method
--------------------------|-------------|--------------------
Aggregation Latency       | <1s         | Event → Redis update
Metrics API Response      | <50ms       | With L2 cache hit
Complex Query Response    | <500ms      | With query cache miss
Cache Hit Rate            | >80%        | Redis INFO stats
Prediction API Response   | <200ms      | Model loaded in memory
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Maintained By:** Architecture Team
