

from faker import Faker
# extensions.py
from mongoengine import connect

mongo = connect  # alias for clarity in create_app

fake = Faker()

from flask_jwt_extended import JWTManager
jwt = JWTManager()