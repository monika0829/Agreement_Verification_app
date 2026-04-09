"""Admin configuration for all apps."""
from django.contrib import admin
from .users.models.user import User
from .agreements.models.vendor import Vendor, Agreement, RateConfiguration, Invoice, InvoiceDiscrepancy
from .verification.models.workflow import VerificationRequest, VerificationCheck
from .compliance.models.rules import ComplianceRule, ComplianceCheck, ComplianceReport

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_code', 'name', 'email', 'city', 'state', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'vendor_code', 'email']

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ['agreement_number', 'vendor', 'agreement_type', 'title', 'status', 'agreement_start_date', 'agreement_end_date']
    list_filter = ['status', 'agreement_type']
    search_fields = ['agreement_number', 'title', 'vendor__name']

@admin.register(RateConfiguration)
class RateConfigurationAdmin(admin.ModelAdmin):
    list_display = ['rate_code', 'rate_name', 'agreement', 'rate_type', 'rate', 'is_active']
    list_filter = ['rate_type', 'is_active']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'vendor', 'agreement', 'status', 'invoice_date', 'total_amount']
    list_filter = ['status', 'invoice_date']
    search_fields = ['invoice_number', 'vendor__name']

@admin.register(InvoiceDiscrepancy)
class InvoiceDiscrepancyAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'discrepancy_type', 'financial_impact', 'is_resolved']
    list_filter = ['discrepancy_type', 'is_resolved']

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'request_type', 'title', 'status', 'result', 'assigned_to']
    list_filter = ['status', 'result', 'request_type']

@admin.register(ComplianceRule)
class ComplianceRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_code', 'rule_name', 'rule_type', 'category', 'severity', 'is_active']
    list_filter = ['rule_type', 'category', 'severity', 'is_active']
