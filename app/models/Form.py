from mongoengine import (
    Document, EmbeddedDocument,
    StringField, ListField, EmbeddedDocumentField,
    ReferenceField, DateTimeField, IntField, BooleanField,
    DictField, UUIDField
)
import uuid
from datetime import datetime, timezone

from app.models.enumerations import FIELD_API_CALL_CHOICES, FIELD_TYPE_CHOICES,FORM_STATUS_CHOICES,ui_TYPE_CHOICES

# --- Response Template model ---
class ResponseTemplate(EmbeddedDocument):
    name = StringField(required=True)
    description = StringField()
    structure = StringField()  # JSON schema or HTML maybe, depending on use case
    tags = ListField(StringField())  # Tags for categorization
    meta_data = DictField()

class ApprovalStep(EmbeddedDocument):
    id = UUIDField(default=uuid.uuid4, binary=False)
    name = StringField(required=True)
    required_role = StringField(required=True) # Role required to approve this step
    order = IntField(default=0)

class Option(EmbeddedDocument):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    description = StringField()
    is_default = BooleanField(default=False)
    is_disabled = BooleanField(default=False)
    option_label = StringField(max_length=255, required=True)
    option_value = StringField(max_length=255, required=True)
    order = IntField(default=0)
    followup_visibility_condition = StringField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

class Question(EmbeddedDocument):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    label = StringField(required=True)
    field_type = StringField(choices=FIELD_TYPE_CHOICES, required=True)  # e.g., "text", "number", "radio", etc.
    is_required = BooleanField(default=False)
    help_text = StringField()
    default_value = StringField()
    order = IntField()
    visibility_condition = StringField()
    validation_rules = StringField()
    required_condition = StringField()  # Condition to make internal field mandatory
    is_repeatable_question = BooleanField(default=False)
    repeat_min = IntField(default=0)
    repeat_max = IntField()

    onChange = StringField()
    calculated_value = StringField()
    is_disabled = BooleanField(default=False)
    
    visible_header = BooleanField(default=False)
    visible_name = StringField()

    # New additions
    response_templates = ListField(EmbeddedDocumentField(ResponseTemplate))
    options = ListField(EmbeddedDocumentField(Option))

    field_api_call = StringField(choices=FIELD_API_CALL_CHOICES)
    custom_script = StringField()  # Custom script for field behavior

    meta_data = DictField()
    required_condition = StringField()  # Field-level required condition

    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

# --- Section model ---
class Section(EmbeddedDocument):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    title = StringField(required=True)
    description = StringField()
    order = IntField()  # Optional: for ordering
    visibility_condition = StringField()
    validation_rules = StringField()
    is_disabled = BooleanField(default=False)
    ui = StringField(choices=ui_TYPE_CHOICES, default="flex")

    is_repeatable_section = BooleanField(default=False)
    repeat_min = IntField(default=0)
    repeat_max = IntField()

    # New additions
    questions = ListField(EmbeddedDocumentField(Question))
    response_templates = ListField(EmbeddedDocumentField(ResponseTemplate))

    meta_data = DictField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

class FormVersion(EmbeddedDocument):
    version=StringField(default="1.0",required=True)
    created_by = StringField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    sections = ListField(EmbeddedDocumentField(Section))
    custom_validations = ListField(DictField()) # [{expression, error_message}]
    translations = DictField() # {lang_code: {title, description, sections: {id: {title, description}}, questions: {id: {label, help_text, options: {id: label}}}}}
    status = StringField(choices=('draft', 'active', 'deprecated'), default='active')

# --- Main Form model ---
class Form(Document):
    meta = {'collection': 'forms'}

    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    title = StringField(max_length=255, required=True)
    description = StringField()
    slug = StringField(max_length=255, required=True, unique=True)
    created_by = StringField(required=True)
    status = StringField(choices=FORM_STATUS_CHOICES, default="draft")
    ui = StringField(choices=ui_TYPE_CHOICES, default="flex")
    submit_scripts = StringField()
    active_version = StringField() # Store version string like "1.1" or "1.0"

    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    expires_at = DateTimeField()
    publish_at = DateTimeField()  # Optional: Auto-publish / available from this date

    is_template = BooleanField(default=False)
    is_public= BooleanField(default=False)
    
    supported_languages = ListField(StringField(), default=["en"])
    default_language = StringField(default="en")
    
    versions = ListField(EmbeddedDocumentField(FormVersion))

    # New additions
    tags = ListField(StringField())
    response_templates = ListField(EmbeddedDocumentField(ResponseTemplate))

    # Permissions
    editors = ListField(StringField())         # Users who can edit
    viewers = ListField(StringField())         # Users who can view/read
    submitters = ListField(StringField())      # Users who can submit responses

    webhooks = ListField(DictField())          # List of webhook configs: {url, event, secret}
    notification_emails = ListField(StringField())  # List of emails to notify on valid submission
    
    approval_enabled = BooleanField(default=False)
    approval_steps = ListField(EmbeddedDocumentField(ApprovalStep))

    # M-11/M-12/M-17 Additions
    title_i18n = DictField()  # {'en': 'Title', 'es': 'Título'}
    style = DictField()       # JSON bucket for styling
    workflows = DictField()   # JSON bucket for workflow rules
    
    @property
    def is_published(self):
        return self.status == 'published'

# --- Individual Response model ---
class FormResponse(Document):
    meta = {
        'collection': 'form_responses',
        'indexes': [
            'form',
            'submitted_by',
            'submitted_at',
            ('form', 'submitted_at'),         # for sorting/pagination
            ('form', 'submitted_by'),         # for user filtering
            'deleted',
            'is_draft',
            ('form', 'is_draft', 'submitted_by')
        ]
    }
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    form = UUIDField(required=True, binary=False)  # Using UUID directly to avoid dereference issues
    data = DictField()  # JSON or stringified object
    submitted_by = StringField()
    submitted_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    updated_by = StringField()
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    deleted = BooleanField(default=False)
    deleted_by = StringField()
    deleted_at = DateTimeField()
    
    is_draft = BooleanField(default=False)
    
    version = StringField()  # Track which form version was used
    
    current_approval_step_index = IntField(default=0)
    approval_history = ListField(DictField()) # {step_id, step_name, approved_by, approved_at, status, comment}
    
    status = StringField(choices=('pending', 'approved', 'rejected'), default='pending')
    status_log = ListField(DictField())  # Log of status changes: {status, changed_by, changed_at, comment}
    
    metadata = DictField()  # IP, browser, device, etc.
    ai_results = DictField() # Sentiment, PII scan, suggestions, etc.


class ResponseHistory(Document):
    meta = {
        'collection': 'response_history',
        'indexes': ['response_id', 'form_id', 'changed_at']
    }
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    response_id = UUIDField(required=True, binary=False)
    form_id = UUIDField(required=True, binary=False)
    
    data_before = DictField()
    data_after = DictField()
    
    changed_by = StringField(required=True)
    changed_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    change_type = StringField(choices=('create', 'update', 'delete', 'restore', 'merge'))
    version = StringField()
    metadata = DictField()

class ResponseComment(Document):
    meta = {
        'collection': 'response_comments',
        'indexes': ['response', 'created_at']
    }
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    response = ReferenceField(FormResponse, required=True, reverse_delete_rule=2) # CASCADE
    user_id = StringField(required=True)
    user_name = StringField()
    content = StringField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

class SavedSearch(Document):
    user_id = StringField(required=True)
    form = ReferenceField(Form)
    name = StringField(required=True)
    filters = DictField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

class CustomFieldTemplate(Document):
    meta = {'collection': 'custom_field_templates'}
    user_id = StringField(required=True)
    name = StringField(required=True)
    category = StringField()
    question_data = EmbeddedDocumentField(Question)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


class SearchHistory(Document):
    """
    Search History Model
    
    Stores user search queries for analytics and personalization.
    Enables showing recent searches and tracking popular queries.
    
    Task: M2-EXT-02b - Persist user search history
    """
    meta = {
        'collection': 'search_history',
        'indexes': [
            'user_id',
            'form_id',
            'timestamp',
            ('user_id', 'form_id'),
            ('user_id', 'timestamp'),
            ('form_id', 'timestamp'),
            ('user_id', 'form_id', 'timestamp')
        ]
    }
    
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    user_id = StringField(required=True)
    form_id = UUIDField(required=True, binary=False)
    query = StringField(required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))
    results_count = IntField(default=0)
    
    # Optional metadata about the search
    parsed_intent = DictField()  # Stores parsed query details
    search_type = StringField(default='nlp')  # 'nlp', 'semantic', 'keyword'
    cached = BooleanField(default=False)


class SummarySnapshot(Document):
    """
    Summary Snapshot Model
    
    Stores summary data snapshots for trend analysis across time periods.
    Enables comparison of sentiment, themes, and response counts over time.
    
    Task: M2-EXT-03c - Add summary comparison across time periods
    """
    meta = {
        'collection': 'summary_snapshots',
        'indexes': [
            'form_id',
            'timestamp',
            'period_start',
            'period_end',
            'created_by',
            ('form_id', 'period_end'),
            ('form_id', 'timestamp')
        ]
    }
    
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    form_id = UUIDField(required=True, binary=False)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Period range for this snapshot
    period_start = DateTimeField(required=True)
    period_end = DateTimeField(required=True)
    period_label = StringField()  # e.g., "last 7 days", "2025-01-01 to 2025-01-31"
    
    # Complete summary data
    summary_data = DictField(required=True)
    
    # Metadata
    created_by = StringField(required=True)
    response_count = IntField(default=0)
    strategy_used = StringField()  # extractive, abstractive, hybrid
    
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


class AnomalyThreshold(Document):
    """
    Anomaly Threshold Model
    
    Stores threshold configurations and history for anomaly detection.
    Enables dynamic threshold calculation based on data distribution.
    
    Task: M2-EXT-04b - Add auto-thresholding for anomaly detection
    """
    meta = {
        'collection': 'anomaly_thresholds',
        'indexes': [
            'form_id',
            'timestamp',
            'sensitivity',
            'created_by',
            ('form_id', 'timestamp'),
            ('form_id', 'sensitivity'),
            ('form_id', 'created_at')
        ]
    }
    
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    form_id = UUIDField(required=True, binary=False)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Threshold configuration
    thresholds = DictField(required=True)  # {z_score_2sigma, z_score_3sigma, z_score_4sigma, ...}
    sensitivity = StringField(default='auto')  # "auto", "low", "medium", "high"
    
    # Baseline statistics used for calculation
    baseline_stats = DictField()  # {avg_response_length, std_response_length, avg_sentiment_score, std_sentiment_score}
    
    # Metadata
    created_by = StringField(required=True)
    response_count = IntField(default=0)  # Number of responses used for baseline calculation
    is_manual = BooleanField(default=False)  # Whether this was manually adjusted
    manual_adjustment_reason = StringField()
    
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


class AnomalyBatchScan(Document):
    """
    Anomaly Batch Scan Model
    
    Stores batch scan information for anomaly detection.
    Enables scheduled scans for large form response sets with progress tracking.
    
    Task: M2-EXT-04c - Add batch scanning for anomaly detection
    """
    meta = {
        'collection': 'anomaly_batch_scans',
        'indexes': [
            'form_id',
            'batch_id',
            'status',
            'created_by',
            'started_at',
            'completed_at',
            ('form_id', 'batch_id'),
            ('form_id', 'status'),
            ('batch_id', 'status')
        ]
    }
    
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    form_id = UUIDField(required=True, binary=False)
    batch_id = StringField(required=True, unique=True)
    
    # Scan configuration
    response_ids = ListField(StringField())  # List of response IDs to scan
    scan_config = DictField()  # {detection_types, sensitivity, use_dynamic_thresholds}
    
    # Scan status
    status = StringField(default='pending')  # "pending", "in_progress", "completed", "failed"
    total_responses = IntField(default=0)
    scanned_count = IntField(default=0)
    results_count = IntField(default=0)
    
    # Scan results
    results = DictField()  # Complete scan results
    summary = DictField()  # Summary statistics
    
    # Metadata
    created_by = StringField(required=True)
    started_at = DateTimeField()
    completed_at = DateTimeField()
    error_message = StringField()
    
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
