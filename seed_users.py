from app import create_app
from app.models.User import User
import os

app = create_app()
with app.app_context():
    # Admin User
    admin_username = os.getenv("DEVELOPMENT_ADMIN_USERNAME", "development_admin")
    admin_email = os.getenv("DEVELOPMENT_ADMIN_EMAIL", "development_admin_medicalrecord@aiims.gov.in")
    admin_password = os.getenv("DEVELOPMENT_ADMIN_PASSWORD", "DevelopmentAdmin!@123")

    admin = User.objects(email=admin_email).first()
    if not admin:
        admin = User(
            username=admin_username,
            email=admin_email,
            user_type='employee',
            roles=['admin', 'superadmin', 'creator', 'editor', 'publisher', 'deo', 'manager']
        )
        admin.set_password(admin_password)
        admin.save()
        print(f"Admin user created: {admin_username}")
    else:
        admin.roles = ['admin', 'superadmin', 'creator', 'editor', 'publisher', 'deo', 'manager']
        admin.save()
        print(f"Admin user {admin_username} updated.")

    # Normal User
    user_username = os.getenv("DEVELOPMENT_USER_USERNAME", "development_user")
    user_email = os.getenv("DEVELOPMENT_USER_EMAIL", "development_user_medicalrecord@aiims.gov.in")
    user_password = os.getenv("DEVELOPMENT_USER_PASSWORD", "DevelopmentUser!@123")

    user = User.objects(email=user_email).first()
    if not user:
        user = User(
            username=user_username,
            email=user_email,
            user_type='employee',
            roles=['user']
        )
        user.set_password(user_password)
        user.save()
        print(f"Normal user created: {user_username}")
    else:
        print(f"Normal user {user_username} already exists.")
