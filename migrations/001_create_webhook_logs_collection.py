"""
Migration: 001_create_webhook_logs_collection
Description: Create webhook_logs collection with indexes for reliable webhook delivery tracking
Date: 2026-02-03
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
import os


def upgrade():
    """
    Create the webhook_logs collection and set up indexes.
    """
    # Get MongoDB connection details from environment
    host = os.getenv('MONGO_HOST', 'localhost')
    port = int(os.getenv('MONGO_PORT', 27017))
    db_name = os.getenv('MONGO_DB', 'myflaskdb')
    
    # Connect to MongoDB
    client = MongoClient(host, port)
    db = client[db_name]
    
    # Create the webhook_logs collection (it will be created automatically when first document is inserted)
    # But we'll set up indexes here
    collection = db['webhook_logs']
    
    # Create indexes for efficient querying
    indexes = [
        # Index on URL for filtering by webhook endpoint
        ([('url', ASCENDING)], {'name': 'idx_url'}),
        
        # Index on status for filtering by delivery status
        ([('status', ASCENDING)], {'name': 'idx_status'}),
        
        # Index on created_at for time-based queries
        ([('created_at', DESCENDING)], {'name': 'idx_created_at'}),
        
        # Index on last_attempt for retry queries
        ([('last_attempt', DESCENDING)], {'name': 'idx_last_attempt'}),
        
        # Compound index on URL and status for common queries
        ([('url', ASCENDING), ('status', ASCENDING)], {'name': 'idx_url_status'}),
        
        # Compound index on status and created_at for dashboard queries
        ([('status', ASCENDING), ('created_at', DESCENDING)], {'name': 'idx_status_created_at'}),
    ]
    
    # Create indexes
    for index_spec, index_options in indexes:
        try:
            collection.create_index(index_spec, **index_options)
            print(f"Created index: {index_options['name']}")
        except Exception as e:
            print(f"Warning: Could not create index {index_options['name']}: {e}")
    
    # Create a TTL index to automatically clean up old successful logs (optional)
    # This will remove successful webhook logs older than 30 days
    try:
        collection.create_index(
            [('created_at', ASCENDING)],
            name='idx_ttl_success',
            expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days in seconds
            partialFilterExpression={'status': 'success'}
        )
        print("Created TTL index for successful logs (30 days)")
    except Exception as e:
        print(f"Warning: Could not create TTL index: {e}")
    
    print(f"Migration completed successfully: webhook_logs collection is ready")
    
    # Close connection
    client.close()


def downgrade():
    """
    Rollback: Drop the webhook_logs collection.
    """
    # Get MongoDB connection details from environment
    host = os.getenv('MONGO_HOST', 'localhost')
    port = int(os.getenv('MONGO_PORT', 27017))
    db_name = os.getenv('MONGO_DB', 'myflaskdb')
    
    # Connect to MongoDB
    client = MongoClient(host, port)
    db = client[db_name]
    
    # Drop the collection
    try:
        db.drop_collection('webhook_logs')
        print("Dropped webhook_logs collection")
    except Exception as e:
        print(f"Warning: Could not drop webhook_logs collection: {e}")
    
    # Close connection
    client.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
