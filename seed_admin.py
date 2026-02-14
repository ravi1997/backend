from app import create_app
from app.models.User import User
import os

app = create_app()
with app.app_context():
    admin_username = os.getenv("DEVELOPMENT_ADMIN_USERNAME", "admin")
    admin_email = os.getenv("DEVELOPMENT_ADMIN_EMAIL", "development_admin_medicalrecord@aiims.gov.in")
    admin_password = os.getenv("DEVELOPMENT_ADMIN_PASSWORD", "DevelopmentAdmin!@123")

    # Check if user exists
    user = User.objects(email=admin_email).first()
    if not user:
        user = User(
            username=admin_username,
            email=admin_email,
            user_type='employee',
            roles=['admin', 'superadmin', 'creator', 'editor', 'publisher', 'deo', 'manager']
        )
        user.set_password(admin_password)
        user.save()
        print(f"Admin user created: {admin_username} ({admin_email})")
    else:
        # Update roles if necessary
        user.roles = ['admin', 'superadmin', 'creator', 'editor', 'publisher', 'deo', 'manager']
        user.save()
        print(f"Admin user {admin_username} already exists. Roles updated.")
