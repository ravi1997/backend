from datetime import datetime, timezone
import uuid
from mongoengine import Document, EmbeddedDocument, StringField, ListField, ReferenceField, DateTimeField, EmbeddedDocumentField, UUIDField, IntField, DictField
from app.models.User import User
from app.models.Form import SavedSearch, Form

class DashboardWidget(EmbeddedDocument):
    id = UUIDField(default=uuid.uuid4, binary=False)
    title = StringField()
    type = StringField(choices=('counter', 'list_view', 'chart_bar', 'chart_pie', 'shortcut'), required=True)
    
    # Data Source
    form_ref = ReferenceField(Form)
    saved_search_ref = ReferenceField(SavedSearch)
    
    # Display Config
    size = StringField(choices=('small', 'medium', 'large', 'full_width'), default='medium')
    refresh_interval = IntField(default=300) # seconds
    
    # Type specific config
    aggregation_field = StringField() # for 'counter'
    display_columns = ListField(StringField()) # for 'list_view'
    target_link = StringField() # for 'shortcut'
    
    # Generic config for charts etc
    config = DictField() 

class Dashboard(Document):
    meta = {'collection': 'dashboards'}
    
    title = StringField(required=True)
    slug = StringField(required=True, unique=True)
    description = StringField()
    roles = ListField(StringField()) # e.g. ['admin', 'deo']
    layout = StringField(default="grid")
    widgets = ListField(EmbeddedDocumentField(DashboardWidget))
    
    created_by = ReferenceField(User)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(Dashboard, self).save(*args, **kwargs)
