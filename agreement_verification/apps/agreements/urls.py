"""
URL configuration for Agreement app CRUD views.
"""
from django.urls import path
from . import views_crud, views_auth
from django.contrib.auth.decorators import login_required

# Import the registration view from users app
from apps.users.views import register_view

app_name = 'agreements'

urlpatterns = [
    # Registration
    path('register/', register_view, name='register'),

    # Login/Logout
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),

    # Dashboard (requires login)
    path('', login_required(views_crud.dashboard), name='dashboard'),

    # Vendor URLs
    path('vendors/', login_required(views_crud.vendor_list), name='vendor_list'),
    path('vendors/create/', login_required(views_crud.vendor_create), name='vendor_create'),
    path('vendors/<int:pk>/', login_required(views_crud.vendor_detail), name='vendor_detail'),
    path('vendors/<int:pk>/edit/', login_required(views_crud.vendor_update), name='vendor_update'),
    path('vendors/<int:pk>/delete/', login_required(views_crud.vendor_delete), name='vendor_delete'),

    # Agreement URLs
    path('agreements/', login_required(views_crud.agreement_list), name='agreement_list'),
    path('agreements/create/', login_required(views_crud.agreement_create), name='agreement_create'),
    path('agreements/<int:pk>/', login_required(views_crud.agreement_detail), name='agreement_detail'),
    path('agreements/<int:pk>/edit/', login_required(views_crud.agreement_update), name='agreement_update'),
    path('agreements/<int:pk>/status/', login_required(views_crud.agreement_change_status), name='agreement_change_status'),

    # Rate Configuration URLs
    path('agreements/<int:agreement_pk>/rates/create/', login_required(views_crud.rate_create), name='rate_create'),
    path('rates/<int:pk>/edit/', login_required(views_crud.rate_update), name='rate_update'),
    path('rates/<int:pk>/delete/', login_required(views_crud.rate_delete), name='rate_delete'),

    # Invoice URLs
    path('invoices/', login_required(views_crud.invoice_list), name='invoice_list'),
    path('invoices/create/', login_required(views_crud.invoice_create), name='invoice_create'),
    path('invoices/<int:pk>/', login_required(views_crud.invoice_detail), name='invoice_detail'),
    path('invoices/<int:pk>/verify/', login_required(views_crud.invoice_verify), name='invoice_verify'),
    path('invoices/<int:pk>/approve/', login_required(views_crud.invoice_approve), name='invoice_approve'),

    # Discrepancy URLs
    path('discrepancies/<int:pk>/resolve/', login_required(views_crud.discrepancy_resolve), name='discrepancy_resolve'),

    # Verification URLs
    path('verifications/', login_required(views_crud.verification_list), name='verification_list'),
    path('verifications/<int:pk>/', login_required(views_crud.verification_detail), name='verification_detail'),
]
