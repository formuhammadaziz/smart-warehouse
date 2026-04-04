from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from datetime import timedelta
import json
from inventory.models import Product, RawMaterial, InventoryTransaction
from production.models import ProductionOrder
from .models import Notification


@login_required
def index(request):
    today = timezone.now().date()

    # Summary cards
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(current_stock__lte=F('minimum_stock')).select_related('default_location')
    active_orders = ProductionOrder.objects.filter(status='in_production').count()
    completed_today = ProductionOrder.objects.filter(
        status='completed',
        actual_end__date=today
    ).count()

    # Stock movement chart — last 7 days
    labels = []
    stock_in = []
    stock_out = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        ins = InventoryTransaction.objects.filter(
            transaction_type='IN', date__date=day
        ).aggregate(total=Sum('quantity'))['total'] or 0
        outs = InventoryTransaction.objects.filter(
            transaction_type__in=['OUT', 'PRODUCTION'], date__date=day
        ).aggregate(total=Sum('quantity'))['total'] or 0
        stock_in.append(float(ins))
        stock_out.append(float(outs))

    # Production stats — by status
    production_stats = ProductionOrder.objects.values('status').annotate(count=Count('id'))
    prod_labels = [s['status'].replace('_', ' ').title() for s in production_stats]
    prod_data = [s['count'] for s in production_stats]

    # Top 5 most used raw materials
    top_materials = (
        InventoryTransaction.objects
        .filter(transaction_type='PRODUCTION', raw_material__isnull=False)
        .values('raw_material__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')[:5]
    )
    mat_labels = [m['raw_material__name'] for m in top_materials]
    mat_data = [float(m['total']) for m in top_materials]

    # Recent notifications
    notifications = Notification.objects.filter(is_read=False)[:5]

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products[:5],
        'active_orders': active_orders,
        'completed_today': completed_today,
        'chart_labels': json.dumps(labels),
        'chart_stock_in': json.dumps(stock_in),
        'chart_stock_out': json.dumps(stock_out),
        'prod_labels': json.dumps(prod_labels),
        'prod_data': json.dumps(prod_data),
        'mat_labels': json.dumps(mat_labels),
        'mat_data': json.dumps(mat_data),
        'notifications': notifications,
        'recent_transactions': InventoryTransaction.objects.select_related('product', 'raw_material', 'performed_by').order_by('-date')[:8],
        'recent_orders': ProductionOrder.objects.select_related('product').order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def notifications_view(request):
    notifications = Notification.objects.all()
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, pk):
    notif = Notification.objects.filter(pk=pk).first()
    if notif:
        notif.is_read = True
        notif.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))


@login_required
def mark_all_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    return redirect('dashboard:notifications')
