import pytest
from app import create_app
from app.config import TestingConfig
from mongoengine import connect, disconnect

@pytest.fixture(scope='session')
def app():
    app = create_app(TestingConfig)
    return app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        # Ensure we are connected to the right DB
        db_name = app.config['MONGODB_SETTINGS']['db']
        # Disconnect any existing connections to prevent leaks/conflicts
        disconnect()
        if app.config.get('TESTING'):
            import mongomock
            conn = connect(db_name, host='mongodb://localhost?uuidRepresentation=standard', mongo_client_class=mongomock.MongoClient)
        else:
            conn = connect(db_name, host=app.config['MONGODB_SETTINGS']['host'], port=app.config['MONGODB_SETTINGS']['port'], uuidRepresentation='standard')
            
        conn.drop_database(db_name)
        yield
        disconnect()
