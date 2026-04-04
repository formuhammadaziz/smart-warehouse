from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction
from .models import ProductionOrder, ProductionStage
from .forms import ProductionOrderForm, ProductionStageForm
from inventory.models import BillOfMaterials, InventoryTransaction, RawMaterial
from dashboard.models import Notification

STAGE_ORDER = ['preparation', 'manufacturing', 'quality_check', 'packaging', 'finished']


def _create_stages(order):
    """Create default production stages for an order."""
    for idx, stage_name in enumerate(STAGE_ORDER):
        ProductionStage.objects.create(
            order=order,
            stage_name=stage_name,
            order_index=idx,
            status='pending',
        )


def _deduct_materials(order):
    """Deduct raw materials from inventory based on BOM."""
    bom_items = BillOfMaterials.objects.filter(product=order.product).select_related('raw_material')
    for item in bom_items:
        needed = item.quantity_required * order.quantity
        material = item.raw_material
        material.current_stock -= needed
        material.save()
        InventoryTransaction.objects.create(
            raw_material=material,
            quantity=needed,
            transaction_type='PRODUCTION',
            reference=f'Production Order #{order.order_number}',
            notes=f'Auto-deducted for production order {order.order_number}',
            performed_by=order.created_by,
        )
        if material.is_low_stock:
            if not Notification.objects.filter(
                notification_type='low_stock',
                is_read=False,
                message__startswith=f'Low stock: {material.name} ',
            ).exists():
                Notification.objects.create(
                    notification_type='low_stock',
                    message=f'Low stock: {material.name} has {material.current_stock} {material.unit} after production deduction.',
                )


@login_required
def order_list(request):
    status_filter = request.GET.get('status', '')
    orders = ProductionOrder.objects.select_related('product', 'created_by', 'assigned_to').all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'production/orders.html', {
        'orders': orders,
        'status_choices': ProductionOrder.STATUS_CHOICES,
        'selected_status': status_filter,
    })


@login_required
def order_create(request):
    form = ProductionOrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.created_by = request.user
        order.save()
        _create_stages(order)
        messages.success(request, f'Production order #{order.order_number} created.')
        return redirect('production:order_detail', pk=order.pk)
    return render(request, 'production/order_form.html', {'form': form, 'title': 'New Production Order'})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    stages = order.stages.all()
    bom_items = BillOfMaterials.objects.filter(product=order.product).select_related('raw_material')

    # Check material availability
    material_check = []
    for item in bom_items:
        needed = item.quantity_required * order.quantity
        available = item.raw_material.current_stock
        material_check.append({
            'material': item.raw_material,
            'needed': needed,
            'available': available,
            'sufficient': available >= needed,
        })

    return render(request, 'production/order_detail.html', {
        'order': order,
        'stages': stages,
        'bom_items': bom_items,
        'material_check': material_check,
    })


@login_required
def order_edit(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    form = ProductionOrderForm(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Production order updated.')
        return redirect('production:order_detail', pk=order.pk)
    return render(request, 'production/order_form.html', {'form': form, 'title': 'Edit Order', 'order': order})


@login_required
def order_start(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    if order.status != 'pending':
        messages.error(request, 'Order cannot be started.')
        return redirect('production:order_detail', pk=pk)

    with db_transaction.atomic():
        can_start, missing = order.can_start()
        if not can_start:
            messages.error(request, f'Insufficient materials: {missing}. Cannot start production.')
            Notification.objects.create(
                notification_type='insufficient_materials',
                message=f'Cannot start order #{order.order_number}: insufficient material "{missing}".',
            )
            return redirect('production:order_detail', pk=pk)

        order.status = 'in_production'
        order.actual_start = timezone.now()
        order.save()
        _deduct_materials(order)
        first_stage = order.stages.first()
        if first_stage:
            first_stage.status = 'in_progress'
            first_stage.started_at = timezone.now()
            first_stage.save()

    messages.success(request, f'Production order #{order.order_number} started. Materials deducted.')
    return redirect('production:order_detail', pk=pk)


@login_required
def order_cancel(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    if request.method == 'POST':
        if order.status in ('pending', 'in_production'):
            order.status = 'cancelled'
            order.save()
            messages.success(request, 'Order cancelled.')
        else:
            messages.error(request, 'Cannot cancel this order.')
    return redirect('production:order_list')


@login_required
def stage_update(request, order_pk, stage_pk):
    order = get_object_or_404(ProductionOrder, pk=order_pk)
    stage = get_object_or_404(ProductionStage, pk=stage_pk, order=order)
    form = ProductionStageForm(request.POST or None, instance=stage)

    if request.method == 'POST' and form.is_valid():
        updated_stage = form.save(commit=False)
        updated_stage.performed_by = request.user
        if updated_stage.status == 'in_progress' and not stage.started_at:
            updated_stage.started_at = timezone.now()
        if updated_stage.status == 'completed':
            updated_stage.completed_at = timezone.now()
            # Auto-advance to next stage
            next_stage = order.stages.filter(order_index=stage.order_index + 1).first()
            if next_stage and next_stage.status == 'pending':
                next_stage.status = 'in_progress'
                next_stage.started_at = timezone.now()
                next_stage.save()
            # Check if all stages done
            if not order.stages.exclude(pk=stage.pk).filter(status__in=['pending', 'in_progress']).exists():
                order.status = 'completed'
                order.actual_end = timezone.now()
                order.product.current_stock += order.quantity
                order.product.save()
                order.save()
                Notification.objects.create(
                    notification_type='production_complete',
                    message=f'Production order #{order.order_number} completed. {order.quantity} {order.product.unit} added to stock.',
                )
                messages.success(request, f'Order #{order.order_number} fully completed!')
        updated_stage.save()
        messages.success(request, f'Stage "{stage.get_stage_name_display()}" updated.')
        return redirect('production:order_detail', pk=order_pk)

    return render(request, 'production/stage_update.html', {
        'form': form, 'order': order, 'stage': stage
    })
