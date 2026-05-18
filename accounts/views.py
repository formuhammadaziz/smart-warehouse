from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import LoginForm, RegisterForm, UserEditForm
from .decorators import admin_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, "Noto'g'ri foydalanuvchi nomi yoki parol.")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('accounts:login')


@login_required
@admin_required
def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Foydalanuvchi {user.username} muvaffaqiyatli yaratildi.')
        return redirect('accounts:users')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@admin_required
def users_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'accounts/users.html', {'users': users})


@login_required
@admin_required
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli yangilandi.")
        return redirect('accounts:users')
    return render(request, 'accounts/user_edit.html', {'form': form, 'edit_user': user})


@login_required
@admin_required
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "O'z hisobingizni o'chira olmaysiz.")
        else:
            user.delete()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli o'chirildi.")
        return redirect('accounts:users')
    return render(request, 'accounts/user_confirm_delete.html', {'edit_user': user})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'profile_user': request.user})
