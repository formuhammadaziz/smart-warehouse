from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('inventory/', views.inventory_report, name='inventory'),
    path('production/', views.production_report, name='production'),
    path('export/inventory/csv/', views.export_inventory_csv, name='export_inventory_csv'),
    path('export/inventory/excel/', views.export_inventory_excel, name='export_inventory_excel'),
    path('export/production/csv/', views.export_production_csv, name='export_production_csv'),
    path('export/production/excel/', views.export_production_excel, name='export_production_excel'),
]
