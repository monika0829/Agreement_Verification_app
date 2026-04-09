"""Vendor and Agreement models."""
from django.db import models
from django.utils import timezone
from utils.constants import AGREEMENT_STATUS_CHOICES, INVOICE_STATUS_CHOICES, DISCREPANCY_TYPE_CHOICES

class Vendor(models.Model):
    vendor_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='USA')
    tax_id = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendors'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.vendor_code})"

class Agreement(models.Model):
    agreement_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='agreements')
    agreement_type = models.CharField(max_length=50, choices=[
        ('VENDOR', 'Vendor Agreement'),
        ('FREIGHT', 'Freight Agreement'),
        ('SERVICE', 'Service Agreement'),
    ], default='VENDOR')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=AGREEMENT_STATUS_CHOICES, default='DRAFT')
    
    agreement_start_date = models.DateField()
    agreement_end_date = models.DateField()
    currency = models.CharField(max_length=3, default='USD')
    estimated_annual_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_terms = models.CharField(max_length=100, default='Net 30')
    
    account_manager = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, 
                                       related_name='managed_agreements')
    agreement_document = models.FileField(upload_to='agreements/', blank=True, null=True)
    
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_agreements')
    rejection_reason = models.TextField(blank=True)
    
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_agreements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agreements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agreement_number']),
            models.Index(fields=['vendor']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.agreement_number} - {self.vendor.name}"

    @property
    def is_expired(self):
        return self.agreement_end_date < timezone.now().date()

class RateConfiguration(models.Model):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='rates')
    rate_code = models.CharField(max_length=100)
    rate_name = models.CharField(max_length=255)
    rate_type = models.CharField(max_length=50, choices=[
        ('FLAT_RATE', 'Flat Rate'),
        ('PER_MILE', 'Per Mile'),
        ('PER_KG', 'Per Kilogram'),
        ('PER_LB', 'Per Pound'),
    ], default='FLAT_RATE')
    rate = models.DecimalField(max_digits=12, decimal_places=4)
    currency = models.CharField(max_length=3, default='USD')
    origin = models.CharField(max_length=255, blank=True)
    destination = models.CharField(max_length=255, blank=True)
    service_level = models.CharField(max_length=100, blank=True)
    equipment_type = models.CharField(max_length=100, blank=True)
    
    effective_start_date = models.DateField()
    effective_end_date = models.DateField(blank=True, null=True)
    tolerance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rate_configurations'
        unique_together = [['agreement', 'rate_code']]
        ordering = ['rate_code']

    def __str__(self):
        return f"{self.rate_code} - {self.rate} {self.currency}"

    def calculate_cost(self, quantity=1, distance=0, weight=0):
        """Calculate cost based on rate type."""
        base_rate = float(self.rate)
        if self.rate_type == 'FLAT_RATE':
            return base_rate
        elif self.rate_type == 'PER_MILE':
            return base_rate * distance
        elif self.rate_type == 'PER_KG':
            return base_rate * weight
        elif self.rate_type == 'PER_LB':
            return base_rate * (weight * 2.20462)
        return base_rate * quantity

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='invoices')
    agreement = models.ForeignKey(Agreement, on_delete=models.PROTECT, related_name='invoices', null=True, blank=True)
    
    invoice_date = models.DateField()
    due_date = models.DateField()
    currency = models.CharField(max_length=3, default='USD')
    subtotal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=50, choices=INVOICE_STATUS_CHOICES, default='PENDING')
    
    invoice_file = models.FileField(upload_to='invoices/')
    line_items = models.JSONField(default=list, blank=True)
    
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='verified_invoices')
    verification_notes = models.TextField(blank=True)
    
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_invoices')
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['vendor']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.vendor.name}"

    @property
    def balance_due(self):
        return float(self.total_amount) - float(self.amount_paid)

class InvoiceDiscrepancy(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='discrepancies')
    rate_configuration = models.ForeignKey(RateConfiguration, on_delete=models.SET_NULL, null=True, blank=True)
    
    discrepancy_type = models.CharField(max_length=50, choices=DISCREPANCY_TYPE_CHOICES)
    line_item_number = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    
    expected_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    difference = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    difference_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    financial_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoice_discrepancies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.discrepancy_type} - {self.invoice.invoice_number}"
