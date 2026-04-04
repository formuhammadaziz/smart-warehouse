from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('warehouse_manager', 'Warehouse Manager'),
        ('production_manager', 'Production Manager'),
        ('worker', 'Worker'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='worker')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_warehouse_manager(self):
        return self.role == 'warehouse_manager' or self.is_admin

    @property
    def is_production_manager(self):
        return self.role == 'production_manager' or self.is_admin
