from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_create, name='transaction_create'),
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    # Locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),
    # Raw Materials
    path('raw-materials/', views.raw_material_list, name='raw_material_list'),
    path('raw-materials/new/', views.raw_material_create, name='raw_material_create'),
    path('raw-materials/<int:pk>/edit/', views.raw_material_edit, name='raw_material_edit'),
    path('raw-materials/<int:pk>/delete/', views.raw_material_delete, name='raw_material_delete'),
    # BOM
    path('bom/', views.bom_list, name='bom_list'),
    path('bom/new/', views.bom_create, name='bom_create'),
    path('bom/<int:pk>/delete/', views.bom_delete, name='bom_delete'),
]
