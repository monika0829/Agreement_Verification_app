"""All views for the application."""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .users.models.user import User
from .agreements.models.vendor import Vendor, Agreement, RateConfiguration, Invoice, InvoiceDiscrepancy
from .verification.models.workflow import VerificationRequest
from .compliance.models.rules import ComplianceRule
from .serializers import (
    UserSerializer, VendorSerializer, AgreementSerializer, 
    RateConfigurationSerializer, InvoiceSerializer, InvoiceDiscrepancySerializer,
    VerificationRequestSerializer, ComplianceRuleSerializer
)
from utils.helpers import is_within_tolerance, generate_reference_number
import pandas as pd

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'vendor_code', 'email']
    ordering_fields = ['name', 'created_at']

class AgreementViewSet(viewsets.ModelViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vendor', 'status', 'agreement_type']
    search_fields = ['agreement_number', 'title', 'vendor__name']
    ordering_fields = ['created_at', 'agreement_start_date']

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        agreement = self.get_object()
        agreement.status = 'SUBMITTED'
        agreement.submitted_at = timezone.now()
        agreement.save()
        return Response({'message': 'Agreement submitted'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        agreement = self.get_object()
        agreement.status = 'APPROVED'
        agreement.approved_by = request.user
        agreement.approved_at = timezone.now()
        agreement.save()
        return Response({'message': 'Agreement approved'})

class RateConfigurationViewSet(viewsets.ModelViewSet):
    queryset = RateConfiguration.objects.all()
    serializer_class = RateConfigurationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['agreement', 'rate_type', 'is_active']
    search_fields = ['rate_code', 'rate_name']

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vendor', 'agreement', 'status']
    search_fields = ['invoice_number', 'vendor__name']
    ordering_fields = ['invoice_date', 'due_date']

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify invoice against agreement rates."""
        invoice = self.get_object()
        
        if not invoice.agreement:
            return Response({'error': 'No agreement associated'}, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = 'PROCESSING'
        invoice.save()
        
        discrepancies_found = False
        line_items = invoice.line_items or []
        
        for item in line_items:
            # Find matching rate
            rate = invoice.agreement.rates.filter(
                is_active=True,
                service_level__icontains=item.get('service_type', '')
            ).first()
            
            if not rate:
                continue
            
            expected_cost = rate.calculate_cost(
                quantity=item.get('quantity', 1),
                distance=item.get('distance', 0),
                weight=item.get('weight', 0)
            )
            actual_cost = item.get('amount', 0)
            
            if not is_within_tolerance(expected_cost, actual_cost, float(rate.tolerance_percentage)):
                InvoiceDiscrepancy.objects.create(
                    invoice=invoice,
                    rate_configuration=rate,
                    discrepancy_type='TOLERANCE_EXCEEDED',
                    description=f"Amount mismatch for {item.get('description', '')}",
                    expected_value=expected_cost,
                    actual_value=actual_cost,
                    difference=abs(actual_cost - expected_cost),
                    financial_impact=abs(actual_cost - expected_cost)
                )
                discrepancies_found = True
        
        invoice.status = 'DISCREPANCY' if discrepancies_found else 'VERIFIED'
        invoice.verified_by = request.user
        invoice.verified_at = timezone.now()
        invoice.save()
        
        return Response({
            'status': invoice.status,
            'message': 'Invoice verified' + ' with discrepancies' if discrepancies_found else ''
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status != 'VERIFIED':
            return Response({'error': 'Only verified invoices can be approved'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        invoice.status = 'APPROVED'
        invoice.approved_by = request.user
        invoice.approved_at = timezone.now()
        invoice.save()
        return Response({'message': 'Invoice approved'})

class InvoiceDiscrepancyViewSet(viewsets.ModelViewSet):
    queryset = InvoiceDiscrepancy.objects.all()
    serializer_class = InvoiceDiscrepancySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['invoice', 'discrepancy_type', 'is_resolved']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        discrepancy = self.get_object()
        discrepancy.is_resolved = True
        discrepancy.resolved_by = request.user
        discrepancy.resolved_at = timezone.now()
        discrepancy.resolution_notes = request.data.get('notes', '')
        discrepancy.save()
        return Response({'message': 'Discrepancy resolved'})

class VerificationRequestViewSet(viewsets.ModelViewSet):
    queryset = VerificationRequest.objects.all()
    serializer_class = VerificationRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['request_type', 'status', 'result', 'assigned_to']
    search_fields = ['reference_number', 'title']

    def perform_create(self, serializer):
        ref_number = generate_reference_number('VR')
        serializer.save(reference_number=ref_number, created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        vr = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            vr.assigned_to = user
            vr.assigned_at = timezone.now()
            vr.save()
            return Response({'message': f'Assigned to {user.email}'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        vr = self.get_object()
        vr.status = 'IN_PROGRESS'
        vr.started_at = timezone.now()
        vr.save()
        return Response({'message': 'Verification started'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        vr = self.get_object()
        vr.status = 'COMPLETED'
        vr.completed_at = timezone.now()
        vr.result = request.data.get('result', 'PASSED')
        vr.save()
        return Response({'message': 'Verification completed'})

class ComplianceRuleViewSet(viewsets.ModelViewSet):
    queryset = ComplianceRule.objects.all()
    serializer_class = ComplianceRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['rule_type', 'category', 'severity', 'is_active']
    search_fields = ['rule_code', 'rule_name']
    ordering_fields = ['execution_order', 'rule_code']
