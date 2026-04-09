"""Verification workflow models."""
from django.db import models
from django.utils import timezone
from utils.constants import VERIFICATION_STATUS_CHOICES, VERIFICATION_RESULT_CHOICES

class VerificationRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('AGREEMENT', 'Agreement Verification'),
        ('INVOICE', 'Invoice Verification'),
    ]

    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES)
    reference_number = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    agreement = models.ForeignKey('agreements.Agreement', on_delete=models.CASCADE, 
                                 related_name='verification_requests', null=True, blank=True)
    invoice = models.ForeignKey('agreements.Invoice', on_delete=models.CASCADE,
                               related_name='verification_requests', null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=VERIFICATION_STATUS_CHOICES, default='PENDING')
    result = models.CharField(max_length=50, choices=VERIFICATION_RESULT_CHOICES, default='PENDING')
    
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ], default='MEDIUM')
    
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_verifications')
    assigned_at = models.DateTimeField(blank=True, null=True)
    
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    
    verification_report = models.JSONField(default=dict, blank=True)
    total_checks = models.PositiveIntegerField(default=0)
    passed_checks = models.PositiveIntegerField(default=0)
    failed_checks = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_verifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'verification_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"Verification {self.reference_number}"

class VerificationCheck(models.Model):
    verification_request = models.ForeignKey(VerificationRequest, on_delete=models.CASCADE, related_name='checks')
    check_name = models.CharField(max_length=255)
    check_code = models.CharField(max_length=100)
    
    status = models.CharField(max_length=50, choices=VERIFICATION_RESULT_CHOICES, default='PENDING')
    severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ], default='MEDIUM')
    
    message = models.TextField(blank=True)
    expected_result = models.TextField(blank=True)
    actual_result = models.TextField(blank=True)
    
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'verification_checks'
        ordering = ['display_order']

    def __str__(self):
        return f"{self.check_code} - {self.check_name}"

class ApprovalWorkflow(models.Model):
    WORKFLOW_TYPE_CHOICES = [
        ('AGREEMENT_APPROVAL', 'Agreement Approval'),
        ('INVOICE_APPROVAL', 'Invoice Approval'),
    ]

    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPE_CHOICES)
    workflow_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    workflow_steps = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'approval_workflows'

    def __str__(self):
        return self.workflow_name

class ApprovalProcess(models.Model):
    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.PROTECT, related_name='processes')
    entity_type = models.CharField(max_length=100)
    entity_id = models.PositiveIntegerField()
    reference_number = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    
    current_step = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, choices=[
        ('IN_PROGRESS', 'In Progress'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='IN_PROGRESS')
    
    requested_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='approval_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='completed_approvals')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'approval_processes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Approval {self.reference_number}"
