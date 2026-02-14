from mongoengine import (
    Document, StringField, ListField, DateTimeField, IntField, DictField, UUIDField, BooleanField
)
import uuid
from datetime import datetime, timezone

class TranslationJob(Document):
    meta = {
        'collection': 'translation_jobs',
        'indexes': [
            'form_id',
            'status',
            'created_by',
            'created_at'
        ]
    }
    
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id = StringField(required=True)
    source_language = StringField(required=True)
    target_languages = ListField(StringField(), required=True)
    status = StringField(choices=('pending', 'inProgress', 'completed', 'failed', 'cancelled'), default='pending')
    progress = IntField(default=0)
    total_fields = IntField(default=0)
    completed_fields = IntField(default=0)
    failed_fields = IntField(default=0)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    started_at = DateTimeField()
    completed_at = DateTimeField()
    created_by = StringField(required=True)
    error_message = StringField()
    results = DictField() # {lang_code: {success_count, failure_count, success, error_message}}

    def to_dict(self):
        return {
            'id': self.id,
            'formId': self.form_id,
            'sourceLanguage': self.source_language,
            'targetLanguages': self.target_languages,
            'status': self.status,
            'progress': self.progress,
            'totalFields': self.total_fields,
            'completedFields': self.completed_fields,
            'failedFields': self.failed_fields,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'createdBy': self.created_by,
            'errorMessage': self.error_message,
            'results': self.results
        }
