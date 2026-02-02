from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask_compress import Compress
from flask_cors import CORS

from app.routes import register_blueprints

from .config import Config
from .extensions import  mongo,jwt
from .models import *



def configure_logging(app):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    if not app.logger.handlers:
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=10240,
            backupCount=5
        )
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info("Logging configured.")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set upload folder configuration
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    configure_logging(app)
    app.logger.info("Using config: %s", config_class.__name__)
    jwt.init_app(app)

    # Init MongoDB
    try:
        mongo_settings = app.config['MONGODB_SETTINGS']
        db_name = mongo_settings['db']
        host = mongo_settings.get('host')
        port = mongo_settings.get('port')
        auth_source = mongo_settings.get('auth_source') or 'admin'
        # Fall back to init variables so docker secrets still work if the app env is missing
        username = mongo_settings.get('username') or os.getenv("MONGO_INITDB_ROOT_USERNAME")
        password = mongo_settings.get('password') or os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        use_auth = bool(username and password)

        mongo_kwargs = {
            'alias': 'default',
            'db': db_name,
            'host': host,
            'port': port,
            'uuidRepresentation': 'standard',
        }

        if use_auth:
            mongo_kwargs.update({
                'username': username,
                'password': password,
                'authentication_source': auth_source,
            })
        else:
            app.logger.warning(
                "MongoDB credentials are missing; attempting unauthenticated connection to %s:%s/%s",
                host,
                port,
                db_name,
            )

        if app.config.get('TESTING'):
            import mongomock
            mongo(db_name, host='mongodb://localhost', mongo_client_class=mongomock.MongoClient, uuidRepresentation='standard')
            app.logger.info("MongoDB connected via MOCK")
        else:
            mongo(**mongo_kwargs)
            app.logger.info(
                "MongoDB connected (auth=%s): host=%s:%s db=%s authSource=%s",
                "enabled" if use_auth else "disabled",
                host,
                port,
                db_name,
                auth_source if use_auth else "n/a",
            )

        if not app.config.get('TESTING'):
            client_kwargs = {
                'host': host,
                'port': port,
                'uuidRepresentation': 'standard',
            }

            if use_auth:
                client_kwargs.update({
                    'username': username,
                    'password': password,
                    'authSource': auth_source,
                })

            with MongoClient(**client_kwargs) as client:
                client.admin.command('ping')
                print("✅ MongoDB connection successful.")
                app.logger.info("✅ MongoDB connection successful.")

    except ConnectionFailure as e:
        app.logger.error("❌ MongoDB connection failed: %s", e)
    except Exception as e:
        app.logger.exception("❌ MongoDB connection failed: %s", e)

    Compress(app)
    CORS(app, 
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization", "Set-Cookie"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"])
    app.logger.info("Middleware loaded: Compress, CORS")

    try:
        register_blueprints(app)
        app.logger.info("Blueprints registered.")
    except Exception as e:
        app.logger.exception("Error registering blueprints: %s", e)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.objects(jti=jti).first()
        return token is not None

    app.logger.info("✅ Flask app created successfully.")
    return app
