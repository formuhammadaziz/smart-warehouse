"""
Quick setup script: creates superuser + loads fixtures.
Run: python setup.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_warehouse.settings')
django.setup()

from django.core.management import call_command
from accounts.models import CustomUser


def main():
    print("=== Smart Warehouse Setup ===\n")

    print("[1/3] Running migrations...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("      Migrations done.\n")

    print("[2/3] Loading sample fixtures...")
    try:
        call_command('loaddata', 'fixtures/initial_data.json', verbosity=0)
        print("      Fixtures loaded.\n")
    except Exception as e:
        print(f"      Warning: {e}\n")

    print("[3/3] Creating default users...")
    users = [
        dict(username='admin',     password='admin123',     role='admin',               first_name='Admin',     last_name='User',    email='admin@warehouse.com',     is_superuser=True, is_staff=True),
        dict(username='wmanager',  password='warehouse123', role='warehouse_manager',   first_name='Warehouse', last_name='Manager', email='wm@warehouse.com'),
        dict(username='pmanager',  password='prod123',      role='production_manager',  first_name='Production',last_name='Manager', email='pm@warehouse.com'),
        dict(username='worker1',   password='worker123',    role='worker',              first_name='John',      last_name='Worker',  email='worker1@warehouse.com'),
    ]
    for u in users:
        if not CustomUser.objects.filter(username=u['username']).exists():
            pw = u.pop('password')
            obj = CustomUser.objects.create_user(password=pw, **u)
            print(f"      Created: {obj.username} ({obj.get_role_display()})")
        else:
            print(f"      Already exists: {u['username']}")

    print("\n=== Setup Complete! ===")
    print("\nDefault accounts:")
    print("  admin     / admin123     (Admin)")
    print("  wmanager  / warehouse123 (Warehouse Manager)")
    print("  pmanager  / prod123      (Production Manager)")
    print("  worker1   / worker123    (Worker)")
    print("\nStart server: python manage.py runserver")
    print("Open: http://127.0.0.1:8000/")


if __name__ == '__main__':
    main()
