from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('warehouse_manager', 'Ombor boshqaruvchisi'),
        ('production_manager', 'Ishlab chiqarish boshqaruvchisi'),
        ('worker', 'Ishchi'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='worker', verbose_name='Rol')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    department = models.CharField(max_length=100, blank=True, verbose_name="Bo'lim")
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
