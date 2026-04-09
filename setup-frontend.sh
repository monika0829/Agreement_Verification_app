#!/bin/bash
# Setup and deploy the frontend for Agreement Verification Application

echo "=== Agreement Verification Frontend Setup ==="
echo ""

# Copy frontend to Django static files
echo "1. Copying frontend to Django static directory..."
mkdir -p /workspace/agreement_verification/static
cp -r /workspace/frontend-static/* /workspace/agreement_verification/static/

echo "2. Creating Django view for frontend..."
cat > /workspace/agreement_verification/apps/views_frontend.py << 'PYEND'
"""Frontend views."""
from django.shortcuts import render
from django.views.generic import TemplateView

class FrontendView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
PYEND

echo "3. Updating Django URL configuration..."
cat > /workspace/agreement_verification/config/urls.py << 'PYEND'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from apps.views_frontend import FrontendView

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
            "admin": "/admin/"
        }
    })

urlpatterns = [
    path('', FrontendView.as_view(), name='home'),
    path('api/', api_root),
    path('admin/', admin.site.urls),
    path('api/v1/auth/login/', TokenObtainPairView.as_view()),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view()),
    path('api/v1/', include('apps.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
PYEND

echo "4. Updating Django settings for templates..."
cat >> /workspace/agreement_verification/config/settings.py << 'PYEND'

# Templates
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'static'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
PYEND

echo "5. Installing frontend dependencies..."
cd /workspace/frontend && npm install --silent 2>/dev/null || echo "npm install available but not required for static version"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Frontend deployed to Django static files."
echo ""
echo "To start the application:"
echo "  cd /workspace/agreement_verification"
echo "  source /workspace/venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo "Then access: http://localhost:8000"
echo ""
echo "Default credentials:"
echo "  Email: admin@example.com"
echo "  Password: Admin123!"
