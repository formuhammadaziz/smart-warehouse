import os
from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create default admin user if not exists'

    def handle(self, *args, **kwargs):
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        email = os.environ.get('ADMIN_EMAIL', 'admin@warehouse.com')

        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(f'Admin "{username}" allaqachon mavjud.')
        else:
            CustomUser.objects.create_superuser(
                username=username,
                password=password,
                email=email,
                role='admin',
                first_name='Admin',
                last_name='User',
            )
            self.stdout.write(self.style.SUCCESS(f'Admin "{username}" yaratildi!'))
