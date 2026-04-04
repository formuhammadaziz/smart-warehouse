from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_admin:
            return func(request, *args, **kwargs)
        messages.error(request, 'Admin access required.')
        return redirect('dashboard:index')
    return wrapper


def warehouse_manager_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_warehouse_manager:
            return func(request, *args, **kwargs)
        messages.error(request, 'Warehouse Manager access required.')
        return redirect('dashboard:index')
    return wrapper


def production_manager_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_production_manager:
            return func(request, *args, **kwargs)
        messages.error(request, 'Production Manager access required.')
        return redirect('dashboard:index')
    return wrapper
