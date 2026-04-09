from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from apps.views_frontend import FrontendView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

def api_root(request):
    return JsonResponse({
        "message": "Agreement Verification API",
        "version": "v1",
        "endpoints": {
            "auth": "/api/v1/auth/login/",
            "vendors": "/api/v1/vendors/",
            "agreements": "/api/v1/agreements/",
            "invoices": "/api/v1/invoices/",
            "verifications": "/api/v1/verifications/",
            "web": "/app/",
            "admin": "/admin/"
        }
    })

def redirect_to_app(request):
    """Redirect root to the web application."""
    return redirect('/app/')

@csrf_exempt
def custom_admin_logout(request):
    """
    Custom admin logout that accepts both GET and POST.
    Django 5+ default logout only accepts POST for security,
    but this causes 405 errors when accessed via GET.
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('/admin/')

urlpatterns = [
    path('', redirect_to_app, name='home'),
    path('api/', api_root),
    # Custom admin logout that accepts both GET and POST
    # Must come before admin.site.urls to override the default logout
    path('admin/logout/', custom_admin_logout, name='admin-logout'),
    path('admin/', admin.site.urls),
    path('api/v1/auth/login/', TokenObtainPairView.as_view()),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view()),
    path('api/v1/', include('apps.api_urls')),
    path('app/', include('apps.agreements.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
