import sys
import os

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.User import User

def list_users():
    users = User.objects()
    print(f"{'ID':<40} | {'Username':<15} | {'Department':<15} | {'Roles':<15}")
    print("-" * 95)
    for u in users:
        print(f"{str(u.id):<40} | {u.username:<15} | {str(u.department):<15} | {', '.join(u.roles):<15}")

def set_department(username, department):
    user = User.objects(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return
    
    user.department = department
    user.save()
    print(f"Success: User '{username}' assigned to department '{department}'.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        if len(sys.argv) < 2:
            print("Usage:")
            print("  python manage_departments.py list")
            print("  python manage_departments.py set <username> <department>")
            sys.exit(1)
        
        command = sys.argv[1]
        
        if command == "list":
            list_users()
        elif command == "set" and len(sys.argv) == 4:
            set_department(sys.argv[2], sys.argv[3])
        else:
            print("Invalid command or arguments.")
