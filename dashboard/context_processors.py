from .models import Notification


def notifications_processor(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:10]
        unread_count = Notification.objects.filter(is_read=False).count()
        return {
            'unread_notifications': unread_notifications,
            'unread_count': unread_count,
        }
    return {}
