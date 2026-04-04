from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/start/', views.order_start, name='order_start'),
    path('orders/<int:pk>/cancel/', views.order_cancel, name='order_cancel'),
    path('orders/<int:order_pk>/stages/<int:stage_pk>/update/', views.stage_update, name='stage_update'),
]
