from django.db import models
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('low_stock', 'Low Stock Alert'),
        ('production_complete', 'Production Completed'),
        ('insufficient_materials', 'Insufficient Materials'),
        ('general', 'General'),
    ]

    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.notification_type}] {self.message[:60]}'
