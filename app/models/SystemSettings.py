import uuid
from datetime import datetime, timezone
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateTimeField, DictField
)


class SystemSettings(Document):
    """
    Singleton-style document that stores backend configuration that can be
    updated dynamically by a superadmin via the API.

    Only one document should exist per environment (keyed by `env_key`).
    """
    meta = {
        'collection': 'system_settings',
        'indexes': [
            {'fields': ['env_key'], 'unique': True},
        ]
    }

    env_key = StringField(required=True, default='default')

    # ── JWT / Auth Settings ─────────────────────────────────────────────
    jwt_access_token_expires_minutes = IntField(default=60)       # minutes
    jwt_refresh_token_expires_days = IntField(default=30)          # days
    max_failed_login_attempts = IntField(default=5)
    account_lock_duration_hours = IntField(default=24)
    password_expiration_days = IntField(default=90)
    otp_expiration_minutes = IntField(default=5)
    max_otp_resends = IntField(default=5)

    # ── File Upload Settings ─────────────────────────────────────────────
    max_upload_size_mb = IntField(default=10)
    allowed_upload_extensions = StringField(
        default='pdf,docx,xlsx,jpg,jpeg,png,gif,svg,mp4,mp3'
    )

    # ── Cache Settings ───────────────────────────────────────────────────
    cache_enabled = BooleanField(default=True)
    cache_default_ttl_seconds = IntField(default=300)
    cache_form_schema_ttl_seconds = IntField(default=3600)
    cache_user_session_ttl_seconds = IntField(default=1800)
    cache_query_result_ttl_seconds = IntField(default=300)
    cache_dashboard_widget_ttl_seconds = IntField(default=120)
    cache_api_response_ttl_seconds = IntField(default=60)

    # ── LLM / AI Settings ───────────────────────────────────────────────
    llm_provider = StringField(default='ollama')
    llm_api_url = StringField(default='http://ollama:11434/v1')
    llm_model = StringField(default='llama3')
    ollama_api_url = StringField(default='http://localhost:11434')
    ollama_embedding_model = StringField(default='nomic-embed-text')
    ollama_pool_size = IntField(default=5)
    ollama_pool_timeout_seconds = IntField(default=30)
    ollama_connection_timeout_seconds = IntField(default=10)

    # ── Redis Settings ───────────────────────────────────────────────────
    redis_host = StringField(default='localhost')
    redis_port = IntField(default=6379)
    redis_db = IntField(default=0)
    redis_max_connections = IntField(default=50)
    redis_socket_timeout_seconds = IntField(default=5)

    # ── CORS / Security ──────────────────────────────────────────────────
    cors_enabled = BooleanField(default=True)
    debug_mode = BooleanField(default=False)
    rate_limit_enabled = BooleanField(default=True)
    rate_limit_requests_per_minute = IntField(default=100)

    # ── Audit ────────────────────────────────────────────────────────────
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_by = StringField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    @classmethod
    def get_or_create_default(cls):
        """Return the singleton settings doc, creating it if absent."""
        doc = cls.objects(env_key='default').first()
        if not doc:
            doc = cls(env_key='default')
            doc.save()
        return doc

    def to_dict(self):
        return {
            'id': str(self.id),
            'env_key': self.env_key,

            # Auth / JWT
            'jwt_access_token_expires_minutes': self.jwt_access_token_expires_minutes,
            'jwt_refresh_token_expires_days': self.jwt_refresh_token_expires_days,
            'max_failed_login_attempts': self.max_failed_login_attempts,
            'account_lock_duration_hours': self.account_lock_duration_hours,
            'password_expiration_days': self.password_expiration_days,
            'otp_expiration_minutes': self.otp_expiration_minutes,
            'max_otp_resends': self.max_otp_resends,

            # File Upload
            'max_upload_size_mb': self.max_upload_size_mb,
            'allowed_upload_extensions': self.allowed_upload_extensions,

            # Cache
            'cache_enabled': self.cache_enabled,
            'cache_default_ttl_seconds': self.cache_default_ttl_seconds,
            'cache_form_schema_ttl_seconds': self.cache_form_schema_ttl_seconds,
            'cache_user_session_ttl_seconds': self.cache_user_session_ttl_seconds,
            'cache_query_result_ttl_seconds': self.cache_query_result_ttl_seconds,
            'cache_dashboard_widget_ttl_seconds': self.cache_dashboard_widget_ttl_seconds,
            'cache_api_response_ttl_seconds': self.cache_api_response_ttl_seconds,

            # LLM / AI
            'llm_provider': self.llm_provider,
            'llm_api_url': self.llm_api_url,
            'llm_model': self.llm_model,
            'ollama_api_url': self.ollama_api_url,
            'ollama_embedding_model': self.ollama_embedding_model,
            'ollama_pool_size': self.ollama_pool_size,
            'ollama_pool_timeout_seconds': self.ollama_pool_timeout_seconds,
            'ollama_connection_timeout_seconds': self.ollama_connection_timeout_seconds,

            # Redis
            'redis_host': self.redis_host,
            'redis_port': self.redis_port,
            'redis_db': self.redis_db,
            'redis_max_connections': self.redis_max_connections,
            'redis_socket_timeout_seconds': self.redis_socket_timeout_seconds,

            # Security / CORS
            'cors_enabled': self.cors_enabled,
            'debug_mode': self.debug_mode,
            'rate_limit_enabled': self.rate_limit_enabled,
            'rate_limit_requests_per_minute': self.rate_limit_requests_per_minute,

            # Audit
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
        }
