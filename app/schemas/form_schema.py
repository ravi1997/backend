from marshmallow import Schema, fields, validate, post_load, pre_load
from uuid import UUID
import uuid

from app.models.enumerations import FIELD_API_CALL_CHOICES, FIELD_TYPE_CHOICES, FORM_STATUS_CHOICES, ui_TYPE_CHOICES
from marshmallow import Schema, fields

# --- ResponseTemplate Schema ---
class ResponseTemplateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    structure = fields.Str(allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)
    meta_data = fields.Dict(allow_none=True)

# --- Option Schema ---
class OptionSchema(Schema):
    id = fields.UUID(required=True)
    description = fields.Str(allow_none=True)
    is_default = fields.Bool(load_default=False)
    is_disabled = fields.Bool(load_default=False)
    option_label = fields.Str(required=True)
    option_value = fields.Str(required=True)
    order = fields.Int(load_default=0)
    followup_visibility_condition = fields.Str()
    created_at = fields.DateTime(dump_only=True)

# --- Question Schema ---
class QuestionSchema(Schema):
    id = fields.UUID(required=True)
    label = fields.Str(required=True)
    field_type = fields.Str(data_key="type", validate=validate.OneOf(FIELD_TYPE_CHOICES), required=True)
    is_required = fields.Bool(data_key="isRequired", load_default=False)
    is_read_only = fields.Bool(data_key="isReadOnly", load_default=False)
    is_hidden = fields.Bool(data_key="isHidden", load_default=False)
    help_text = fields.Str(data_key="helperText", allow_none=True)
    default_value = fields.Str(allow_none=True)
    order = fields.Int()
    visibility_condition = fields.Str()
    validation_rules = fields.Str()
    is_repeatable_question = fields.Bool(load_default=False)
    repeat_min = fields.Int(load_default=0)
    repeat_max = fields.Int()
    onChange = fields.Str()
    calculated_value = fields.Str()
    is_disabled = fields.Bool(load_default=False)
    visible_header = fields.Bool(load_default=False)
    visible_name = fields.Str()
    response_templates = fields.List(fields.Nested(ResponseTemplateSchema))
    options = fields.List(fields.Nested(OptionSchema), allow_none=True)
    field_api_call = fields.Str(validate=validate.OneOf(FIELD_API_CALL_CHOICES), allow_none=True)
    custom_script = fields.Str(allow_none=True)
    placeholder = fields.Str(allow_none=True)
    meta_data = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = "EXCLUDE"

    @pre_load
    def handle_localized_fields(self, data, **kwargs):
        for field in ['label', 'helperText', 'placeholder']:
            if field in data and isinstance(data[field], dict):
                data[field] = data[field].get('en') or next(iter(data[field].values()), "")
        return data

# --- Section Schema ---
class SectionSchema(Schema):
    id = fields.UUID(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    order = fields.Int(allow_none=True)
    visibility_condition = fields.Str(allow_none=True)
    validation_rules = fields.Str(allow_none=True)
    is_disabled = fields.Bool(load_default=False)
    ui = fields.Str(validate=validate.OneOf(ui_TYPE_CHOICES), load_default="flex")
    is_repeatable_section = fields.Bool(load_default=False)
    repeat_min = fields.Int(load_default=0)
    repeat_max = fields.Int(allow_none=True)
    questions = fields.List(fields.Nested(QuestionSchema))
    response_templates = fields.List(fields.Nested(ResponseTemplateSchema))
    meta_data = fields.Dict()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = "EXCLUDE"

    @pre_load
    def handle_localized_fields(self, data, **kwargs):
        for field in ['title', 'description']:
            if field in data and isinstance(data[field], dict):
                data[field] = data[field].get('en') or next(iter(data[field].values()), "")
        return data

# --- FormVersion Schema ---
class FormVersionSchema(Schema):
    version = fields.Str(required=True)
    created_by = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    sections = fields.List(fields.Nested(SectionSchema))
    status = fields.Str(validate=validate.OneOf(('draft', 'active', 'deprecated')), load_default='active')
    custom_validations = fields.List(fields.Dict())
    translations = fields.Dict()

    class Meta:
        unknown = "EXCLUDE"

# --- Form Schema ---
class FormSchema(Schema):
    id = fields.UUID(required=True)
    title = fields.Str(required=True)
    description = fields.Str()
    slug = fields.Str(required=True)
    created_by = fields.Str(required=True)
    status = fields.Str(validate=validate.OneOf(FORM_STATUS_CHOICES), load_default="draft")
    ui = fields.Str(validate=validate.OneOf(ui_TYPE_CHOICES), load_default="flex")
    submit_scripts = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_public = fields.Bool(load_default=False)
    versions = fields.List(fields.Nested(FormVersionSchema))
    tags = fields.List(fields.Str())
    response_templates = fields.List(fields.Nested(ResponseTemplateSchema))
    editors = fields.List(fields.Str())
    uiers = fields.List(fields.Str())
    submitters = fields.List(fields.Str())
    active_version = fields.Str()

    class Meta:
        unknown = "EXCLUDE"

    @pre_load
    def handle_localized_fields(self, data, **kwargs):
        if 'title' in data and isinstance(data['title'], dict):
            data['title'] = data['title'].get('en') or next(iter(data['title'].values()), "Untitled Form")
        return data

# --- FormResponse Schema ---
class FormResponseSchema(Schema):
    id = fields.UUID(required=True)
    form = fields.UUID(required=True)  # Assuming you want just the form ID
    data = fields.Dict()
    submitted_by = fields.Str()
    submitted_at = fields.DateTime(dump_only=True)
    updated_by = fields.Str()
    updated_at = fields.DateTime(dump_only=True)
    deleted = fields.Bool(load_default=False)
    deleted_by = fields.Str()
    deleted_at = fields.DateTime(dump_only=True)
    metadata = fields.Dict()
