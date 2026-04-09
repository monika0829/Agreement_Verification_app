"""API v1 URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, VendorViewSet, AgreementViewSet, RateConfigurationViewSet,
    InvoiceViewSet, InvoiceDiscrepancyViewSet, VerificationRequestViewSet,
    ComplianceRuleViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'agreements', AgreementViewSet, basename='agreement')
router.register(r'rates', RateConfigurationViewSet, basename='rate')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'invoice-discrepancies', InvoiceDiscrepancyViewSet, basename='invoice-discrepancy')
router.register(r'verifications', VerificationRequestViewSet, basename='verification')
router.register(r'compliance-rules', ComplianceRuleViewSet, basename='compliance-rule')

urlpatterns = [
    path('', include(router.urls)),
]
