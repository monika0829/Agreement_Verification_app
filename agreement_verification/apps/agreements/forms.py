"""Forms for Agreement app with validation."""
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Vendor, Agreement, RateConfiguration, Invoice, InvoiceDiscrepancy
import re


class VendorForm(forms.ModelForm):
    """Form for Vendor CRUD operations."""

    class Meta:
        model = Vendor
        fields = [
            'vendor_code', 'name', 'email', 'phone', 'address',
            'city', 'state', 'country', 'tax_id', 'is_active'
        ]
        widgets = {
            'vendor_code': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'E.g., VEN-001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Company name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'vendor@company.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+1-234-567-8900'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Country'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Tax ID / EIN'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_vendor_code(self):
        code = self.cleaned_data.get('vendor_code')
        if not re.match(r'^[A-Z0-9\-]+$', code.upper()):
            raise ValidationError('Vendor code must contain only uppercase letters, numbers, and hyphens.')
        return code.upper()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower()


class AgreementForm(forms.ModelForm):
    """Form for Agreement CRUD operations."""

    class Meta:
        model = Agreement
        fields = [
            'agreement_number', 'vendor', 'agreement_type', 'title',
            'description', 'agreement_start_date', 'agreement_end_date',
            'currency', 'estimated_annual_value', 'payment_terms',
            'account_manager', 'agreement_document'
        ]
        widgets = {
            'agreement_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'E.g., AG-2024-001'
            }),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'agreement_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Agreement title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
            'agreement_start_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'agreement_end_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'estimated_annual_value': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Net 30'
            }),
            'account_manager': forms.Select(attrs={'class': 'form-select'}),
            'agreement_document': forms.FileInput(attrs={
                'class': 'form-control', 'accept': '.pdf,.doc,.docx'
            }),
        }

    def clean_agreement_number(self):
        number = self.cleaned_data.get('agreement_number')
        if not re.match(r'^[A-Z0-9\-]+$', number.upper()):
            raise ValidationError('Agreement number must contain only uppercase letters, numbers, and hyphens.')
        return number.upper()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('agreement_start_date')
        end_date = cleaned_data.get('agreement_end_date')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('End date must be after start date.')

        return cleaned_data


class RateConfigurationForm(forms.ModelForm):
    """Form for Rate Configuration CRUD operations."""

    class Meta:
        model = RateConfiguration
        fields = [
            'rate_code', 'rate_name', 'rate_type', 'rate', 'currency',
            'origin', 'destination', 'service_level', 'equipment_type',
            'effective_start_date', 'effective_end_date', 'tolerance_percentage', 'is_active'
        ]
        widgets = {
            'rate_code': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'E.g., RATE-001'
            }),
            'rate_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Rate description'
            }),
            'rate_type': forms.Select(attrs={'class': 'form-select'}),
            'rate': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.0001', 'placeholder': '0.0000'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'origin': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Origin location'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Destination location'
            }),
            'service_level': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'E.g., Standard, Express'
            }),
            'equipment_type': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'E.g., 53ft, Refrigerated'
            }),
            'effective_start_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'effective_end_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'tolerance_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_rate_code(self):
        code = self.cleaned_data.get('rate_code')
        return code.upper()


class InvoiceForm(forms.ModelForm):
    """Form for Invoice upload and management."""

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'vendor', 'agreement', 'invoice_date',
            'due_date', 'currency', 'subtotal_amount', 'tax_amount',
            'total_amount', 'invoice_file'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'INV-2024-001'
            }),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'agreement': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'subtotal_amount': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'value': '0.00'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'
            }),
            'invoice_file': forms.FileInput(attrs={
                'class': 'form-control', 'accept': '.pdf,.xlsx,.xls,.png,.jpg'
            }),
        }

    def clean_invoice_number(self):
        number = self.cleaned_data.get('invoice_number')
        return number.upper()

    def clean_invoice_file(self):
        file = self.cleaned_data.get('invoice_file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg']:
                raise ValidationError('Only PDF, Excel, and image files are allowed.')
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError('File size must not exceed 10MB.')
        return file


class InvoiceVerificationForm(forms.Form):
    """Form for invoice verification with notes."""

    verification_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Add verification notes, findings, or comments...'
        })
    )

    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve Invoice'),
            ('reject', 'Reject Invoice'),
            ('request_info', 'Request More Information'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Provide reason for rejection...'
        })
    )


class InvoiceDiscrepancyForm(forms.ModelForm):
    """Form for discrepancy resolution."""

    class Meta:
        model = InvoiceDiscrepancy
        fields = ['resolution_notes', 'is_resolved']
        widgets = {
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Explain how this discrepancy was resolved...'
            }),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ApprovalActionForm(forms.Form):
    """Form for approval/rejection actions."""

    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('return', 'Return for Changes'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add comments for your decision...'
        })
    )


class AgreementStatusForm(forms.Form):
    """Form for changing agreement status."""

    status = forms.ChoiceField(
        choices=[
            ('DRAFT', 'Draft'),
            ('PENDING_APPROVAL', 'Submit for Approval'),
            ('ACTIVE', 'Activate'),
            ('ON_HOLD', 'Put on Hold'),
            ('EXPIRED', 'Mark as Expired'),
            ('TERMINATED', 'Terminate'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Provide reason for status change...'
        })
    )
