import bcrypt
from marshmallow import Schema, fields, validate, post_load, EXCLUDE
from sqlalchemy import null
from app.models.User import User, UserType, Role
from marshmallow_enum import EnumField


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore extra fields on load

    id = fields.String(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    mobile = fields.String(required=True, validate=validate.Length(min=10))
    employee_id = fields.String(required=False, allow_none=True)
    user_type = fields.String(
        required=True,
        validate=validate.OneOf([e.value for e in UserType])
    )
    roles = fields.List(
        fields.String(validate=validate.OneOf([r.value for r in Role])),
        required=True
    )
    
    # Auth & status
    password = fields.String(load_only=True, required=True)
    is_active = fields.Boolean(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    is_email_verified = fields.Boolean(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # OTP-related fields (only shown if explicitly needed)
    otp = fields.String(allow_none=True)
    otp_expiration = fields.DateTime(allow_none=True)
    failed_login_attempts = fields.Integer(dump_only=True)
    otp_resend_count = fields.Integer(dump_only=True)
    lock_until = fields.DateTime(dump_only=True)
    password_expiration = fields.DateTime(dump_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        if 'password' in data:
            salt = bcrypt.gensalt()
            data['password_hash'] = bcrypt.hashpw(data.pop('password').encode(), salt).decode()
        user = User(**data)
        return user
