import uuid
import bcrypt
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from flask import current_app
from mongoengine import (
    Document, StringField, EmailField, DateTimeField,
    BooleanField, ListField, IntField
)

# -------------------- Config --------------------

MAX_FAILED_ATTEMPTS = 5
MAX_OTP_RESENDS = 5
LOCK_DURATION_HOURS = 24
PASSWORD_EXPIRATION_DAYS = 90

# Logger Setup
logger = logging.getLogger("auth")
logging.basicConfig(level=logging.INFO)

# -------------------- Enums --------------------


class UserType(str, Enum):
    EMPLOYEE = 'employee'
    GENERAL = 'general'


class Role(str, Enum):

    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    USER = 'user'

    CREATOR = 'creator'                # CAN CREATE A FORM
    EDITOR = 'editor'                  # CANNOT CREATE A FORM
    PUBLISHER = 'publisher'            # CAN PUBLISH THE FORM
    DEO = 'deo'
    GENERAL = 'general'

# -------------------- Model --------------------


class User(Document):
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['username'], 'unique': True, 'sparse': True},
            {'fields': ['email'], 'unique': True, 'sparse': True},
            {'fields': ['employee_id'], 'unique': True, 'sparse': True},
            {'fields': ['mobile'], 'unique': True, 'sparse': True}
        ]
    }

    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    username = StringField(max_length=50)
    email = EmailField()
    employee_id = StringField(max_length=30)
    mobile = StringField(max_length=15)
    user_type = StringField(required=True, choices=[e.value for e in UserType])
    password_hash = StringField(max_length=255)
    password_expiration = DateTimeField()
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    is_email_verified = BooleanField(default=False)
    roles = ListField(StringField(
        choices=[r.value for r in Role]), default=list)
    failed_login_attempts = IntField(default=0)
    otp_resend_count = IntField(default=0)
    lock_until = DateTimeField()
    last_login = DateTimeField()
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    otp = StringField(max_length=6)
    otp_expiration = DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    # -------------------- Security Methods --------------------

    def is_locked(self) -> bool:
        return self.lock_until and datetime.now(timezone.utc) < self.lock_until

    def lock_account(self):
        self.lock_until = datetime.now(
            timezone.utc) + timedelta(hours=LOCK_DURATION_HOURS)
        logger.warning(f"User {self.id} locked until {self.lock_until}")
        self.save()

    def unlock_account(self):
        self.lock_until = None
        self.failed_login_attempts = 0
        self.otp_resend_count = 0
        logger.info(f"User {self.id} manually unlocked")
        self.save()

    def increment_failed_logins(self):
        if self.is_locked():
            return
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            self.lock_account()
        else:
            self.update(set__failed_login_attempts=self.failed_login_attempts)

    def reset_failed_logins(self):
        self.failed_login_attempts = 0

    def resend_otp(self):
        if self.is_locked():
            return
        self.otp_resend_count += 1
        if self.otp_resend_count >= MAX_OTP_RESENDS:
            self.lock_account()
        else:
            self.update(set__otp_resend_count=self.otp_resend_count)

    def set_otp(self, otp_code: str, ttl_minutes: int = 5):
        self.otp = otp_code
        self.otp_expiration = datetime.now(
            timezone.utc) + timedelta(minutes=ttl_minutes)
        self.otp_resend_count = 0

    def verify_otp(self, code: str) -> bool:
        current_app.logger.info(
            f"Verifying OTP for user {self.id}. Provided: {code}, Expected: {self.to_dict(include_sensitive=True)}")
        if self.is_locked():
            current_app.logger.warning(
                f"OTP verification failed: user {self.id} is locked.")
            return False

        otp_exp = self.otp_expiration
        if otp_exp and otp_exp.tzinfo is None:
            otp_exp = otp_exp.replace(tzinfo=timezone.utc)

        if not otp_exp or otp_exp <= datetime.now(timezone.utc):
            current_app.logger.warning(
                f"OTP expired for user {self.id}. Provided: {code}, Expected: {self.otp}")
            return False

        if self.otp != code:
            current_app.logger.warning(
                f"Invalid OTP for user {self.id}. Provided: {code}, Expected: {self.otp}")
            return False

        current_app.logger.info(
            f"✅ OTP verified successfully for user {self.id}")
        return True

    def set_password(self, raw_password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            raw_password.encode(), salt).decode()
        self.password_expiration = datetime.now(
            timezone.utc) + timedelta(days=PASSWORD_EXPIRATION_DAYS)

    def check_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(raw_password.encode(), self.password_hash.encode())
        except Exception:
            return False

    def is_password_expired(self) -> bool:
        return self.password_expiration and datetime.now(timezone.utc) > self.password_expiration

    # -------------------- Roles --------------------

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def is_superadmin_check(self) -> bool:
        return Role.SUPERADMIN.value in self.roles

    def is_admin_check(self) -> bool:
        return Role.ADMIN.value in self.roles or self.is_superadmin_check()

    # -------------------- Login --------------------

    @staticmethod
    def authenticate(identifier: str, password: str) -> "User | None":
        """
        Employee login via username/email/employee_id + password.
        """
        user = User.objects(
            user_type=UserType.EMPLOYEE.value,
            is_active=True,
            __raw__={"$or": [
                {"username": identifier},
                {"email": identifier},
                {"employee_id": identifier}
            ]}
        ).first()

        if not user:
            return None

        if user.is_locked():
            logger.warning(f"Login blocked: User {user.id} is locked")
            return None

        if not user.check_password(password):
            user.increment_failed_logins()
            return None

        if user.is_password_expired():
            logger.warning(f"User {user.id} password expired")
            return None

        user.last_login = datetime.now(timezone.utc)
        user.reset_failed_logins()
        user.save()
        logger.info(f"Successful login for user {user.id}")
        return user

    @staticmethod
    def authenticate_with_otp(mobile: str, otp_code: str) -> "User | None":
        """
        Mobile OTP login (general and employee allowed).
        """
        user = User.objects(mobile=mobile, is_active=True).first()

        if not user or user.is_locked():
            return None

        if not user.verify_otp(otp_code):
            user.increment_failed_logins()
            return None

        user.last_login = datetime.utcnow()
        user.reset_failed_logins()
        user.save()
        logger.info(f"Successful OTP login for user {user.id}")
        return user

    # -------------------- Serialization --------------------

    def to_dict(self, include_sensitive=False):
        def iso_or_none(dt):
            return dt.isoformat() if dt else None

        data = {
            'id': self.id,
            'user_type': self.user_type,
            'username': self.username,
            'email': self.email,
            'employee_id': self.employee_id,
            'mobile': self.mobile,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_email_verified': self.is_email_verified,
            'roles': self.roles,
            'failed_login_attempts': self.failed_login_attempts,
            'otp_resend_count': self.otp_resend_count,
            'lock_until': iso_or_none(self.lock_until),
            'created_at': iso_or_none(self.created_at),
            'updated_at': iso_or_none(self.updated_at),
            'last_login': iso_or_none(self.last_login),
            'password_expiration': iso_or_none(self.password_expiration),
        }

        if include_sensitive:
            data.update({
                'password_hash': self.password_hash,
                'otp': self.otp,
                'otp_expiration': iso_or_none(self.otp_expiration),
            })

        return data

    def __str__(self):
        return f"<User(username='{self.username}', type='{self.user_type}')>"
