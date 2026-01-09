# Implementation Plan: Phase 1 Foundation
## Event-Driven Architecture & Multi-Tenancy

**Phase:** P1 - Foundation  
**Duration Estimate:** 3-4 weeks (Sprint planning: 2-week sprints)  
**Team Size:** 2-3 developers + 1 DevOps engineer  

---

## Sprint 1: Infrastructure & Multi-Tenancy (Week 1-2)

### Sprint Goal
Set up event infrastructure and implement multi-tenancy data model.

---

### Task 1.1: Environment & Infrastructure Setup
**Estimated Time:** 4 hours  
**Assignee:** DevOps Engineer  
**Priority:** Critical (Blocking)

#### Steps:
1. **Update `docker-compose.yml`**
   ```yaml
   services:
     redis:
       image: redis:7.2-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
       command: redis-server --appendonly yes
       healthcheck:
         test: ["CMD", "redis-cli", "ping"]
         interval: 10s
         timeout: 3s
         retries: 3
     
     celery_worker:
       build: .
       command: celery -A celery_worker.celery worker --loglevel=info --concurrency=4
       depends_on:
         - redis
         - mongo
       environment:
         - CELERY_BROKER_URL=redis://redis:6379/0
         - CELERY_RESULT_BACKEND=redis://redis:6379/0
       volumes:
         - .:/app
   
   volumes:
     redis_data:
   ```

2. **Update `requirements.txt`**
   ```txt
   celery[redis]==5.3.4
   redis==5.0.1
   blinker==1.7.0
   flower==2.0.1  # Optional: Celery monitoring
   ```

3. **Create `.env.example` additions**
   ```bash
   # Task Queue Configuration
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   CELERY_TASK_TRACK_STARTED=True
   CELERY_TASK_TIME_LIMIT=300
   
   # Multi-Tenancy
   DEFAULT_TENANT_ID=default
   ENABLE_TENANT_ISOLATION=True
   ```

4. **Verify Setup**
   ```bash
   docker-compose up -d redis
   docker-compose logs redis
   # Should see: "Ready to accept connections"
   ```

#### Acceptance Criteria:
- [ ] Redis container starts successfully
- [ ] Redis persists data after restart (AOF enabled)
- [ ] Dependencies install without conflicts
- [ ] Environment variables documented

---

### Task 1.2: Database Schema Migration Planning
**Estimated Time:** 6 hours  
**Assignee:** Backend Developer 1  
**Priority:** Critical (Blocking)

#### Steps:

1. **Create Migration Script Structure**
   ```
   app/migrations/
   ├── __init__.py
   ├── migration_001_add_tenant_id.py
   └── migration_manager.py
   ```

2. **Implement `migration_001_add_tenant_id.py`**
   ```python
   """
   Migration: Add tenant_id to all collections
   Date: 2026-01-09
   """
   import os
   from datetime import datetime
   from pymongo import MongoClient, UpdateOne
   from app.database import db
   
   DEFAULT_TENANT = os.getenv('DEFAULT_TENANT_ID', 'default')
   
   COLLECTIONS = ['users', 'forms', 'form_versions', 'form_responses', 'files']
   
   def backup_collection(collection_name):
       """Create timestamped backup"""
       backup_name = f"{collection_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
       db[collection_name].aggregate([{"$out": backup_name}])
       return backup_name
   
   def migrate_collection(collection_name):
       """Add tenant_id to all documents"""
       collection = db[collection_name]
       
       # Count documents
       total = collection.count_documents({})
       print(f"Migrating {total} documents in {collection_name}...")
       
       # Backup first
       backup_name = backup_collection(collection_name)
       print(f"Backup created: {backup_name}")
       
       # Bulk update
       bulk_ops = []
       cursor = collection.find({"tenant_id": {"$exists": False}})
       
       for doc in cursor:
           bulk_ops.append(
               UpdateOne(
                   {"_id": doc["_id"]},
                   {"$set": {
                       "tenant_id": DEFAULT_TENANT,
                       "migrated_at": datetime.utcnow()
                   }}
               )
           )
           
           # Execute in batches of 1000
           if len(bulk_ops) >= 1000:
               result = collection.bulk_write(bulk_ops)
               print(f"  Updated {result.modified_count} documents...")
               bulk_ops = []
       
       # Execute remaining
       if bulk_ops:
           result = collection.bulk_write(bulk_ops)
           print(f"  Updated {result.modified_count} documents")
       
       # Verify
       migrated = collection.count_documents({"tenant_id": DEFAULT_TENANT})
       print(f"✓ Migration complete: {migrated}/{total} documents")
       
       return migrated == total
   
   def create_indexes(collection_name):
       """Create tenant-scoped indexes"""
       collection = db[collection_name]
       
       # Index mapping
       indexes = {
           'users': [
               ('tenant_id', 1),
               ([('tenant_id', 1), ('email', 1)], {'unique': True}),
           ],
           'forms': [
               ('tenant_id', 1),
               ([('tenant_id', 1), ('slug', 1)], {'unique': True}),
               ([('tenant_id', 1), ('created_at', -1)], {}),
           ],
           'form_responses': [
               ([('tenant_id', 1), ('form_id', 1)], {}),
               ([('tenant_id', 1), ('created_at', -1)], {}),
           ]
       }
       
       if collection_name in indexes:
           for idx in indexes[collection_name]:
               if isinstance(idx, tuple) and len(idx) == 2:
                   collection.create_index(idx[0], **idx[1], background=True)
               else:
                   collection.create_index(idx, background=True)
           print(f"✓ Indexes created for {collection_name}")
   
   def run_migration():
       """Execute migration"""
       print("=" * 60)
       print("Migration 001: Add tenant_id to all collections")
       print("=" * 60)
       
       success = True
       for coll in COLLECTIONS:
           if not migrate_collection(coll):
               success = False
               print(f"✗ Migration failed for {coll}")
               break
           create_indexes(coll)
       
       if success:
           print("\n✓ All migrations completed successfully")
       else:
           print("\n✗ Migration failed - rolling back...")
       
       return success
   
   if __name__ == "__main__":
       run_migration()
   ```

3. **Create Rollback Script**
   ```python
   # migration_001_rollback.py
   def rollback():
       """Restore from backup"""
       # Implementation to restore from latest backup
       pass
   ```

4. **Dry Run Test**
   ```bash
   # Test on development database
   python -m app.migrations.migration_001_add_tenant_id --dry-run
   ```

#### Acceptance Criteria:
- [ ] Migration script backs up all collections
- [ ] All documents get `tenant_id` field
- [ ] Unique indexes created successfully
- [ ] Rollback script tested
- [ ] Migration completes in <10 minutes for 100K documents

---

### Task 1.3: Tenant Model & Utilities
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer 1  
**Priority:** High

#### Steps:

1. **Create `app/models/Tenant.py`**
   ```python
   from datetime import datetime
   from app.database import db
   from bson import ObjectId
   
   class Tenant:
       collection = db['tenants']
       
       @staticmethod
       def create(data):
           """Create new tenant"""
           tenant = {
               'tenant_id': data.get('tenant_id'),  # Unique slug
               'name': data['name'],
               'status': 'active',
               'settings': {
                   'max_forms': data.get('max_forms', 100),
                   'max_responses_per_form': data.get('max_responses', 10000),
                   'features': {
                       'workflows': False,
                       'ai_generation': False,
                       'webhooks': False
                   }
               },
               'created_at': datetime.utcnow(),
               'updated_at': datetime.utcnow()
           }
           result = Tenant.collection.insert_one(tenant)
           tenant['_id'] = result.inserted_id
           return tenant
       
       @staticmethod
       def get_by_tenant_id(tenant_id):
           """Retrieve tenant by tenant_id"""
           return Tenant.collection.find_one({'tenant_id': tenant_id, 'status': 'active'})
       
       @staticmethod
       def exists(tenant_id):
           """Check if tenant exists and is active"""
           return Tenant.collection.count_documents({
               'tenant_id': tenant_id,
               'status': 'active'
           }) > 0
   ```

2. **Create `app/utils/tenant_context.py`**
   ```python
   from flask import g, request, abort
   from functools import wraps
   from app.models.Tenant import Tenant
   
   def get_current_tenant():
       """Get current tenant from Flask context"""
       return getattr(g, 'tenant_id', None)
   
   def require_tenant(f):
       """Decorator to ensure tenant context is set"""
       @wraps(f)
       def decorated_function(*args, **kwargs):
           if not get_current_tenant():
               abort(400, description="Tenant context is required")
           return f(*args, **kwargs)
       return decorated_function
   
   def set_tenant_context(tenant_id):
       """Set tenant in Flask g object"""
       if not Tenant.exists(tenant_id):
               abort(404, description=f"Tenant '{tenant_id}' not found")
       g.tenant_id = tenant_id
   ```

3. **Create Tenant Middleware `app/middleware/tenant_middleware.py`**
   ```python
   from flask import request, g
   from app.utils.tenant_context import set_tenant_context
   import os
   
   class TenantMiddleware:
       def __init__(self, app):
           self.app = app
           app.before_request(self.resolve_tenant)
       
       def resolve_tenant(self):
           """Resolve tenant from various sources"""
           tenant_id = None
           
           # 1. Header
           tenant_id = request.headers.get('X-Tenant-ID')
           
           # 2. JWT (if exists)
           if not tenant_id and hasattr(g, 'user'):
               tenant_id = g.user.get('tenant_id')
           
           # 3. Default fallback for v1 compatibility
           if not tenant_id:
               tenant_id = os.getenv('DEFAULT_TENANT_ID', 'default')
           
           set_tenant_context(tenant_id)
   ```

#### Acceptance Criteria:
- [ ] Tenant model CRUD operations work
- [ ] Middleware resolves tenant correctly
- [ ] Decorator blocks requests without tenant
- [ ] Unit tests pass

---

### Task 1.4: Update Existing Models
**Estimated Time:** 6 hours  
**Assignee:** Backend Developer 2  
**Priority:** High

#### Steps:

1. **Update `app/models/Form.py`** - Add tenant scoping to all queries
   ```python
   from app.utils.tenant_context import get_current_tenant
   
   class Form:
       @staticmethod
       def create(data):
           tenant_id = get_current_tenant()
           form = {
               'tenant_id': tenant_id,
               # ... existing fields
           }
           # Check unique constraint (tenant_id, slug)
           existing = db.forms.find_one({
               'tenant_id': tenant_id,
               'slug': data['slug']
           })
           if existing:
               raise ValueError(f"Form with slug '{data['slug']}' already exists")
           
           return db.forms.insert_one(form)
       
       @staticmethod
       def get_by_id(form_id):
           tenant_id = get_current_tenant()
           return db.forms.find_one({
               '_id': ObjectId(form_id),
               'tenant_id': tenant_id
           })
       
       @staticmethod
       def list_forms(filters=None):
           tenant_id = get_current_tenant()
           query = {'tenant_id': tenant_id}
           if filters:
               query.update(filters)
           return list(db.forms.find(query))
   ```

2. **Update `app/models/FormResponse.py`**
   ```python
   class FormResponse:
       @staticmethod
       def create(data):
           tenant_id = get_current_tenant()
           response = {
               'tenant_id': tenant_id,
               'form_id': data['form_id'],
               # ... existing fields
           }
           return db.form_responses.insert_one(response)
       
       @staticmethod
       def get_by_id(response_id):
           tenant_id = get_current_tenant()
           return db.form_responses.find_one({
               '_id': ObjectId(response_id),
               'tenant_id': tenant_id
           })
   ```

3. **Update User model similarly**

#### Acceptance Criteria:
- [ ] All model queries include `tenant_id` filter
- [ ] Cross-tenant access impossible
- [ ] Unique constraints work per tenant
- [ ] Existing tests updated and passing

---

## Sprint 2: Event System & Async Processing (Week 3-4)

### Sprint Goal
Implement event-driven architecture and migrate heavy operations to background tasks.

---

### Task 2.1: Event System Foundation
**Estimated Time:** 8 hours  
**Assignee:** Backend Developer 1  
**Priority:** Critical

#### Steps:

1. **Create `app/events/signals.py`**
   ```python
   from blinker import Namespace
   
   # Create namespace for our signals
   signals = Namespace()
   
   # Define all events
   form_created = signals.signal('form-created')
   form_updated = signals.signal('form-updated')
   form_archived = signals.signal('form-archived')
   response_submitted = signals.signal('response-submitted')
   response_updated = signals.signal('response-updated')
   user_registered = signals.signal('user-registered')
   ```

2. **Create `app/events/event_dispatcher.py`**
   ```python
   from datetime import datetime
   import uuid
   from flask import g
   from app.utils.tenant_context import get_current_tenant
   
   class EventDispatcher:
       @staticmethod
       def emit(signal, entity_id, payload, metadata=None):
           """Standardized event emission"""
           event_data = {
               'event_id': str(uuid.uuid4()),
               'event_type': signal.name,
               'timestamp': datetime.utcnow().isoformat(),
               'tenant_id': get_current_tenant(),
               'user_id': getattr(g, 'user_id', None),
               'entity_id': str(entity_id),
               'payload': payload,
               'metadata': metadata or {}
           }
           
           # Emit signal (non-blocking)
           signal.send('app', event_data=event_data)
           
           return event_data['event_id']
   ```

3. **Update routes to emit events** - Example: `app/routes/v1/form/responses.py`
   ```python
   from app.events.signals import response_submitted
   from app.events.event_dispatcher import EventDispatcher
   
   @responses_bp.route('/<form_id>/submit', methods=['POST'])
   def submit_response(form_id):
       # Validate and save (existing logic)
       result = FormResponse.create(data)
       response_id = result.inserted_id
       
       # Emit event (NEW)
       EventDispatcher.emit(
           signal=response_submitted,
           entity_id=response_id,
           payload={
               'form_id': form_id,
               'data': data
           }
       )
       
       return jsonify({"response_id": str(response_id)}), 201
   ```

#### Acceptance Criteria:
- [ ] Events emit successfully
- [ ] Event data includes all required fields
- [ ] API response time not affected (< 5ms overhead)
- [ ] Events logged for debugging

---

### Task 2.2: Celery Configuration
**Estimated Time:** 6 hours  
**Assignee:** DevOps + Backend Developer 2  
**Priority:** Critical

#### Steps:

1. **Create `celery_worker.py` in root**
   ```python
   import os
   from celery import Celery
   from app import create_app
   
   # Create Flask app for context
   flask_app = create_app()
   
   # Configure Celery
   celery = Celery(
       'form_backend',
       broker=os.getenv('CELERY_BROKER_URL'),
       backend=os.getenv('CELERY_RESULT_BACKEND')
   )
   
   # Update Celery config
   celery.conf.update(
       task_serializer='json',
       accept_content=['json'],
       result_serializer='json',
       timezone='UTC',
       enable_utc=True,
       task_track_started=True,
       task_time_limit=300,  # 5 minutes
       task_soft_time_limit=240,  # 4 minutes
       worker_prefetch_multiplier=4,
       worker_max_tasks_per_child=1000,
       task_acks_late=True,
       task_reject_on_worker_lost=True,
       task_default_retry_delay=60,  # 1 minute
       task_max_retries=3
   )
   
   # Auto-discover tasks
   celery.autodiscover_tasks(['app.tasks'])
   
   @celery.task(bind=True)
   def debug_task(self):
       print(f'Request: {self.request!r}')
   ```

2. **Create `app/tasks/__init__.py`**
   ```python
   from .email_tasks import send_email, send_bulk_emails
   from .export_tasks import generate_csv_export
   from .webhook_tasks import trigger_webhook
   
   __all__ = [
       'send_email',
       'send_bulk_emails',
       'generate_csv_export',
       'trigger_webhook'
   ]
   ```

3. **Create `app/tasks/email_tasks.py`**
   ```python
   from celery_worker import celery, flask_app
   from app.services.email_service import EmailService
   import logging
   
   logger = logging.getLogger(__name__)
   
   @celery.task(bind=True, max_retries=3)
   def send_email(self, tenant_id, to_email, subject, body, template=None):
       """Send single email"""
       try:
           with flask_app.app_context():
               EmailService.send(
                   to=to_email,
                   subject=subject,
                   body=body,
                   template=template
               )
               logger.info(f"Email sent to {to_email} for tenant {tenant_id}")
               return {'status': 'success', 'recipient': to_email}
       except Exception as exc:
           logger.error(f"Email failed: {exc}")
           raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
   
   @celery.task
   def send_bulk_emails(tenant_id, email_list):
       """Send multiple emails"""
       results = []
       for email_data in email_list:
           result = send_email.delay(
               tenant_id=tenant_id,
               **email_data
           )
           results.append(result.id)
       return results
   ```

#### Acceptance Criteria:
- [ ] Celery worker starts successfully
- [ ] Tasks execute and complete
- [ ] Retry logic works on failures
- [ ] Tasks visible in Flower dashboard

---

### Task 2.3: Event Listeners
**Estimated Time:** 6 hours  
**Assignee:** Backend Developer 2  
**Priority:** High

#### Steps:

1. **Create `app/events/listeners.py`**
   ```python
   from app.events.signals import response_submitted, form_created
   from app.tasks.email_tasks import send_email
   from app.models.Form import Form
   import logging
   
   logger = logging.getLogger(__name__)
   
   @response_submitted.connect
   def on_response_submitted(sender, event_data, **extra):
       """Handle form response submission"""
       logger.info(f"Response submitted: {event_data['event_id']}")
       
       tenant_id = event_data['tenant_id']
       form_id = event_data['payload']['form_id']
       
       # Get form settings
       form = Form.get_by_id(form_id)
       if not form:
           logger.error(f"Form {form_id} not found")
           return
       
       # Send notification email if configured
       if form.get('settings', {}).get('send_notification'):
           send_email.delay(
               tenant_id=tenant_id,
               to_email=form['owner_email'],
               subject=f"New Response: {form['title']}",
               body="A new response has been submitted",
               template='response_notification'
           )
   
   @form_created.connect
   def on_form_created(sender, event_data, **extra):
       """Handle new form creation"""
       logger.info(f"Form created: {event_data['entity_id']}")
       # Future: Send welcome email, update analytics, etc.
   
   def register_listeners():
       """Register all event listeners"""
       logger.info("Event listeners registered")
   ```

2. **Update `app/__init__.py` to register listeners**
   ```python
   def create_app():
       app = Flask(__name__)
       
       # ... existing setup
       
       # Register event listeners
       from app.events.listeners import register_listeners
       register_listeners()
       
       return app
   ```

#### Acceptance Criteria:
- [ ] Listeners trigger on events
- [ ] Tasks queued successfully
- [ ] Email sent in background
- [ ] No impact on API response time

---

### Task 2.4: Migrate Email Sending
**Estimated Time:** 4 hours  
**Assignee:** Backend Developer 1  
**Priority:** Medium

#### Steps:

1. **Identify all email sending code**
   ```bash
   grep -r "EmailService.send" app/routes/
   ```

2. **Replace synchronous calls with async**
   ```python
   # OLD:
   EmailService.send(to=user.email, subject="Welcome", body="...")
   
   # NEW:
   from app.tasks.email_tasks import send_email
   send_email.delay(
       tenant_id=get_current_tenant(),
       to_email=user.email,
       subject="Welcome",
       body="..."
   )
   ```

3. **Update affected routes**:
   - User registration
   - Password reset
   - Form submission notifications
   - Share invitations

#### Acceptance Criteria:
- [ ] All email sends are async
- [ ] API response times improved
- [ ] Emails still delivered successfully
- [ ] Error handling preserved

---

### Task 2.5: Testing & Validation
**Estimated Time:** 8 hours  
**Assignee:** Backend Developer 1 + 2  
**Priority:** High

#### Steps:

1. **Create Integration Tests** - `tests/integration/test_events.py`
   ```python
   import pytest
   from app.events.signals import response_submitted
   from app.events.event_dispatcher import EventDispatcher
   
   def test_event_emission():
       """Test event is emitted with correct structure"""
       received_events = []
       
       @response_submitted.connect
       def capture_event(sender, event_data, **extra):
           received_events.append(event_data)
       
       # Emit event
       EventDispatcher.emit(
           signal=response_submitted,
           entity_id="test-123",
           payload={"form_id": "form-456"}
       )
       
       # Verify
       assert len(received_events) == 1
       assert received_events[0]['entity_id'] == "test-123"
       assert 'event_id' in received_events[0]
       assert 'timestamp' in received_events[0]
   ```

2. **Create Tenant Isolation Tests** - `tests/security/test_tenant_isolation.py`
   ```python
   def test_cross_tenant_access_denied(client):
       """Ensure tenant A cannot access tenant B's data"""
       # Create form for tenant A
       response = client.post('/api/v1/forms', 
           json={'title': 'Form A'},
           headers={'X-Tenant-ID': 'tenant-a'}
       )
       form_id = response.json['form_id']
       
       # Try to access from tenant B
       response = client.get(f'/api/v1/forms/{form_id}',
           headers={'X-Tenant-ID': 'tenant-b'}
       )
       assert response.status_code == 404
   ```

3. **Load Testing** - `tests/load/test_async_performance.py`
   ```python
   def test_submission_performance(benchmark):
       """Verify <100ms response time"""
       def submit_form():
           return client.post('/api/v1/forms/test-form/submit', json={...})
       
       result = benchmark(submit_form)
       assert result.stats['mean'] < 0.1  # 100ms
   ```

4. **Run Full Test Suite**
   ```bash
   pytest tests/ -v --cov=app --cov-report=html
   ```

#### Acceptance Criteria:
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Tenant isolation verified
- [ ] Performance benchmarks met (< 100ms)
- [ ] Code coverage > 85%

---

## Post-Sprint Activities

### Documentation
**Time:** 4 hours

1. **Update API Documentation**
   - Add `X-Tenant-ID` header documentation
   - Document async task response format
   - Add examples for multi-tenant requests

2. **Create Operations Runbook**
   - How to restart Celery workers
   - Redis monitoring commands
   - Troubleshooting event failures

3. **Developer Guide**
   - How to emit new events
   - How to create new Celery tasks
   - Multi-tenancy best practices

### Deployment Preparation

1. **Create Deployment Checklist**
   ```markdown
   ## Pre-Deployment
   - [ ] Full database backup
   - [ ] Test migration on staging
   - [ ] Verify Redis persistence configured
   - [ ] Review rollback procedure
   
   ## Deployment Steps
   - [ ] Enable maintenance mode
   - [ ] Stop application
   - [ ] Run migration script
   - [ ] Start Redis
   - [ ] Start Celery workers (2+ instances)
   - [ ] Start application
   - [ ] Verify health checks
   - [ ] Disable maintenance mode
   
   ## Post-Deployment
   - [ ] Monitor error logs (30 minutes)
   - [ ] Check task queue depth
   - [ ] Verify emails being sent
   - [ ] Run smoke tests
   ```

2. **Monitoring Setup**
   - Set up Flower for Celery monitoring
   - Add Prometheus metrics for queue depth
   - Configure alerts for task failures

---

## Risk Mitigation

### High-Risk Areas

1. **Data Migration**
   - **Risk**: Data loss or corruption during tenant_id backfill
   - **Mitigation**: 
     - Full backup before migration
     - Dry-run on copy of production DB
     - Rollback script ready
     - Migration in maintenance window

2. **Redis Failure**
   - **Risk**: Task queue unavailable
   - **Mitigation**:
     - Redis persistence (AOF)
     - Graceful degradation (API continues working)
     - Monitoring and alerting

3. **Performance Regression**
   - **Risk**: Middleware adds latency
   - **Mitigation**:
     - Tenant caching
     - Load testing before deployment
     - Rollback plan if latency > 100ms

---

## Success Metrics

### Phase 1 Completion Criteria
- [ ] API response time < 100ms (p90)
- [ ] Zero cross-tenant data leakage (security audit passed)
- [ ] All emails sent via async tasks
- [ ] Redis uptime > 99.9%
- [ ] Task success rate > 99%
- [ ] Code coverage > 85%
- [ ] Documentation complete
- [ ] Team trained on new architecture

### Performance Benchmarks
| Metric | Baseline (v1) | Target (P1) | Actual |
|--------|---------------|-------------|--------|
| Form submission (p90) | 480ms | <100ms | _TBD_ |
| Tenant resolution | N/A | <2ms | _TBD_ |
| Event emission | N/A | <5ms | _TBD_ |
| Task failure rate | N/A | <1% | _TBD_ |

---

## Dependencies & Blockers

### External Dependencies
- Redis 7.0+ availability
- MongoDB 5.0+ for transactions
- SMTP server for email delivery

### Internal Dependencies
- DevOps: Docker Compose updates
- Security: Tenant isolation audit
- Frontend: No changes required (backward compatible)

### Potential Blockers
- Production database too large for 4-hour migration window
  - **Solution**: Implement streaming migration
- Existing data has integrity issues
  - **Solution**: Run cleanup scripts first

---

**Next Phase:** [Phase 2 - Workflow Automation](./03_PLAN_PHASE2.md)
