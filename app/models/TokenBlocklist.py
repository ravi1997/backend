from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class TokenBlocklist(Document):
    """
    Stores revoked JWT tokens by their JTI with expiry.
    """
    meta = {
        'collection': 'token_blocklist',
        'indexes': [
            'jti',
            {'fields': ['expires_at'], 'expireAfterSeconds': 0}  # TTL index
        ]
    }

    jti = StringField(required=True, unique=True, max_length=36)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    expires_at = DateTimeField(required=True)  # TTL support
