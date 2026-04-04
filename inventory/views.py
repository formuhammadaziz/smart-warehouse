from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.utils import timezone
from .models import Product, Category, WarehouseLocation, RawMaterial, BillOfMaterials, InventoryTransaction
from .forms import ProductForm, CategoryForm, WarehouseLocationForm, RawMaterialForm, BOMForm, StockTransactionForm
from dashboard.models import Notification


# ─── Products ────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')

    products = Product.objects.select_related('category', 'default_location').all()
    if q:
        products = products.filter(Q(product_name__icontains=q) | Q(sku__icontains=q))
    if category_id:
        products = products.filter(category_id=category_id)
    if status == 'low':
        products = products.filter(current_stock__lte=F('minimum_stock'))
    elif status == 'out':
        products = products.filter(current_stock=0)

    categories = Category.objects.all()
    return render(request, 'inventory/products.html', {
        'products': products,
        'categories': categories,
        'q': q,
        'selected_category': category_id,
        'selected_status': status,
    })


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save()
        messages.success(request, f'Product "{product.product_name}" created.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    transactions = product.transactions.select_related('performed_by', 'warehouse_location').order_by('-date')[:20]
    bom_items = product.bom_items.select_related('raw_material').all()
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'transactions': transactions,
        'bom_items': bom_items,
    })


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})


# ─── Transactions ─────────────────────────────────────────────────────────────

@login_required
def transaction_list(request):
    transactions = InventoryTransaction.objects.select_related(
        'product', 'raw_material', 'warehouse_location', 'performed_by'
    ).order_by('-date')

    q = request.GET.get('q', '')
    tx_type = request.GET.get('type', '')
    if q:
        transactions = transactions.filter(
            Q(product__product_name__icontains=q) |
            Q(raw_material__name__icontains=q) |
            Q(reference__icontains=q)
        )
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)

    return render(request, 'inventory/transactions.html', {
        'transactions': transactions,
        'q': q,
        'selected_type': tx_type,
        'transaction_types': InventoryTransaction.TRANSACTION_TYPES,
    })


@login_required
def transaction_create(request):
    form = StockTransactionForm(request.POST or None, initial={'date': timezone.now()})
    if request.method == 'POST' and form.is_valid():
        tx = form.save(commit=False)
        tx.performed_by = request.user
        tx.save()
        _apply_transaction(tx)
        messages.success(request, 'Transaction recorded successfully.')
        return redirect('inventory:transaction_list')
    return render(request, 'inventory/transaction_form.html', {'form': form, 'title': 'New Transaction'})


def _apply_transaction(tx):
    """Update stock levels based on transaction type."""
    qty = tx.quantity
    if tx.product:
        p = tx.product
        if tx.transaction_type == 'IN':
            p.current_stock += qty
        elif tx.transaction_type in ('OUT', 'PRODUCTION'):
            p.current_stock -= qty
        elif tx.transaction_type == 'ADJUSTMENT':
            p.current_stock = qty
        p.save()
        if p.is_low_stock:
            if not Notification.objects.filter(
                notification_type='low_stock',
                is_read=False,
                message__startswith=f'Low stock alert: {p.product_name} (',
            ).exists():
                Notification.objects.create(
                    notification_type='low_stock',
                    message=f'Low stock alert: {p.product_name} ({p.current_stock} {p.unit} remaining)',
                )
    elif tx.raw_material:
        m = tx.raw_material
        if tx.transaction_type == 'IN':
            m.current_stock += qty
        elif tx.transaction_type in ('OUT', 'PRODUCTION'):
            m.current_stock -= qty
        elif tx.transaction_type == 'ADJUSTMENT':
            m.current_stock = qty
        m.save()
        if m.is_low_stock:
            if not Notification.objects.filter(
                notification_type='low_stock',
                is_read=False,
                message__startswith=f'Low stock alert: {m.name} (',
            ).exists():
                Notification.objects.create(
                    notification_type='low_stock',
                    message=f'Low stock alert: {m.name} ({m.current_stock} {m.unit} remaining)',
                )


# ─── Categories ───────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.all()
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/categories.html', {'categories': categories, 'form': form})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
    return redirect('inventory:category_list')


# ─── Locations ────────────────────────────────────────────────────────────────

@login_required
def location_list(request):
    locations = WarehouseLocation.objects.all()
    form = WarehouseLocationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Location created.')
        return redirect('inventory:location_list')
    return render(request, 'inventory/locations.html', {'locations': locations, 'form': form})


@login_required
def location_delete(request, pk):
    loc = get_object_or_404(WarehouseLocation, pk=pk)
    if request.method == 'POST':
        loc.delete()
        messages.success(request, 'Location deleted.')
    return redirect('inventory:location_list')


# ─── Raw Materials ────────────────────────────────────────────────────────────

@login_required
def raw_material_list(request):
    materials = RawMaterial.objects.select_related('location').all()
    q = request.GET.get('q', '')
    if q:
        materials = materials.filter(Q(name__icontains=q) | Q(code__icontains=q))
    return render(request, 'inventory/raw_materials.html', {'materials': materials, 'q': q})


@login_required
def raw_material_create(request):
    form = RawMaterialForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Raw material created.')
        return redirect('inventory:raw_material_list')
    return render(request, 'inventory/raw_material_form.html', {'form': form, 'title': 'Add Raw Material'})


@login_required
def raw_material_edit(request, pk):
    material = get_object_or_404(RawMaterial, pk=pk)
    form = RawMaterialForm(request.POST or None, instance=material)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Raw material updated.')
        return redirect('inventory:raw_material_list')
    return render(request, 'inventory/raw_material_form.html', {'form': form, 'title': 'Edit Raw Material', 'material': material})


@login_required
def raw_material_delete(request, pk):
    material = get_object_or_404(RawMaterial, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Raw material deleted.')
        return redirect('inventory:raw_material_list')
    return render(request, 'inventory/raw_material_confirm_delete.html', {'material': material})


# ─── BOM ──────────────────────────────────────────────────────────────────────

@login_required
def bom_list(request):
    bom_items = BillOfMaterials.objects.select_related('product', 'raw_material').all()
    return render(request, 'inventory/bom.html', {'bom_items': bom_items})


@login_required
def bom_create(request):
    form = BOMForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'BOM entry created.')
        return redirect('inventory:bom_list')
    return render(request, 'inventory/bom_form.html', {'form': form, 'title': 'Add BOM Entry'})


@login_required
def bom_delete(request, pk):
    bom = get_object_or_404(BillOfMaterials, pk=pk)
    if request.method == 'POST':
        bom.delete()
        messages.success(request, 'BOM entry deleted.')
    return redirect('inventory:bom_list')
