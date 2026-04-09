"""All serializers for the application."""
from rest_framework import serializers
from .users.models.user import User
from .agreements.models.vendor import Vendor, Agreement, RateConfiguration, Invoice, InvoiceDiscrepancy
from .verification.models.workflow import VerificationRequest, VerificationCheck
from .compliance.models.rules import ComplianceRule, ComplianceCheck, ComplianceReport

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# Vendor Serializers
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Agreement Serializers
class AgreementSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    class Meta:
        model = Agreement
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired']

# Rate Serializers
class RateConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateConfiguration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Invoice Serializers
class InvoiceSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.FloatField(read_only=True)
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance_due']

# Invoice Discrepancy Serializers
class InvoiceDiscrepancySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDiscrepancy
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

# Verification Serializers
class VerificationRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    class Meta:
        model = VerificationRequest
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Compliance Serializers
class ComplianceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
