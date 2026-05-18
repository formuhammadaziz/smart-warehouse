from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_admin:
            return func(request, *args, **kwargs)
        messages.error(request, 'Administrator huquqi talab etiladi.')
        return redirect('dashboard:index')
    return wrapper


def warehouse_manager_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_warehouse_manager:
            return func(request, *args, **kwargs)
        messages.error(request, 'Ombor boshqaruvchisi huquqi talab etiladi.')
        return redirect('dashboard:index')
    return wrapper


def production_manager_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_production_manager:
            return func(request, *args, **kwargs)
        messages.error(request, 'Ishlab chiqarish boshqaruvchisi huquqi talab etiladi.')
        return redirect('dashboard:index')
    return wrapper
