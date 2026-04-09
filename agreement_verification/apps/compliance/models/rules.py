"""Compliance rule engine models."""
from django.db import models

class ComplianceRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('VALIDATION', 'Validation Rule'),
        ('BUSINESS_LOGIC', 'Business Logic Rule'),
        ('CALCULATION', 'Calculation Rule'),
    ]

    CATEGORY_CHOICES = [
        ('AGREEMENT', 'Agreement Rules'),
        ('INVOICE', 'Invoice Rules'),
        ('VENDOR', 'Vendor Rules'),
    ]

    rule_code = models.CharField(max_length=100, unique=True)
    rule_name = models.CharField(max_length=255)
    rule_description = models.TextField()
    
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], default='MEDIUM')
    
    is_active = models.BooleanField(default=True)
    rule_config = models.JSONField(default=dict)
    error_message = models.CharField(max_length=500)
    execution_order = models.PositiveIntegerField(default=0)
    is_blocking = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compliance_rules'
        ordering = ['execution_order', 'rule_code']

    def __str__(self):
        return f"{self.rule_code} - {self.rule_name}"

class ComplianceCheck(models.Model):
    rule = models.ForeignKey(ComplianceRule, on_delete=models.PROTECT, related_name='checks')
    entity_type = models.CharField(max_length=100)
    entity_id = models.PositiveIntegerField()
    
    status = models.CharField(max_length=50, choices=[
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('WARNING', 'Warning'),
    ], default='PENDING')
    
    severity = models.CharField(max_length=20, default='MEDIUM')
    passed = models.BooleanField(default=False)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    input_data = models.JSONField(default=dict, blank=True)
    expected_value = models.TextField(blank=True)
    actual_value = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_checks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Check {self.rule.rule_code}"

class ComplianceReport(models.Model):
    entity_type = models.CharField(max_length=100)
    entity_id = models.PositiveIntegerField()
    reference_number = models.CharField(max_length=100)
    
    total_checks = models.PositiveIntegerField(default=0)
    passed_checks = models.PositiveIntegerField(default=0)
    failed_checks = models.PositiveIntegerField(default=0)
    warning_checks = models.PositiveIntegerField(default=0)
    
    overall_status = models.CharField(max_length=50, choices=[
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('WARNING', 'Warning'),
    ], default='PENDING')
    
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    report_data = models.JSONField(default=dict, blank=True)
    findings = models.JSONField(default=list, blank=True)
    
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.reference_number}"
