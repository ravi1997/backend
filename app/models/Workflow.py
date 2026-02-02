from datetime import datetime, timezone
import uuid
from mongoengine import Document, EmbeddedDocument, StringField, ListField, ReferenceField, DateTimeField, EmbeddedDocumentField, UUIDField, BooleanField, DictField
from app.models.Form import Form
from app.models.User import User

class WorkflowAction(EmbeddedDocument):
    type = StringField(choices=('redirect_to_form', 'create_draft', 'notify_user'), required=True)
    
    # For 'redirect_to_form' / 'create_draft':
    target_form_id = StringField() # Stores Form ID string
    
    # Data Mapping: Target Field -> Source Field/Expression
    # Example: {"patient_name": "name", "uhid": "uhid", "reg_date": "submitted_at"}
    data_mapping = DictField() 
    
    # User Assignment (for 'create_draft')
    # Can be a static user ID or a field name in the source form that contains the user ID
    assign_to_user_field = StringField() 

class FormWorkflow(Document):
    meta = {'collection': 'form_workflows'}
    
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    name = StringField(required=True)
    description = StringField()
    
    trigger_form_id = StringField(required=True) # The "Primary" form ID string
    trigger_condition = StringField(default="True") # Python-expression, e.g., "'admit' in answers.get('disposition')"
    
    actions = ListField(EmbeddedDocumentField(WorkflowAction))
    
    is_active = BooleanField(default=True)
    
    created_by = ReferenceField(User)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(FormWorkflow, self).save(*args, **kwargs)
