"""
Authentication views for the web application.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json


@csrf_exempt  # Exempt CSRF for login to work with reverse proxy
def login_view(request):
    """Login page for web application."""
    if request.user.is_authenticated:
        return redirect('/app/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('/app/')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'agreements/login.html')


def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('/app/login/')
