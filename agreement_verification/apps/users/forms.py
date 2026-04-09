"""
Forms for User Registration and Authentication.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User
import re


class UserRegistrationForm(forms.ModelForm):
    """
    User registration form with validation for:
    - Email
    - Password
    - Name (first_name, last_name)
    - GST Number
    - PAN Number
    - Mobile Number
    """

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password'
        }),
        label="Password",
        help_text="Minimum 8 characters with letters and numbers"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        label="Confirm Password"
    )

    # GST Number validator (15 alphanumeric characters)
    gst_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., 29ABCDE1234F1Z5'
        }),
        label="GST Number",
        help_text="15-character GST identification number"
    )

    # PAN Number validator (10 characters: 5 letters + 4 digits + 1 letter)
    pan_number = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., ABCDE1234F',
            'style': 'text-transform: uppercase;'
        }),
        label="PAN Number",
        help_text="10-character Permanent Account Number"
    )

    # Mobile Number validator (10 digits)
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., +91 98765 43210'
        }),
        label="Mobile Number",
        help_text="10-digit mobile number with country code"
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        }),
        label="First Name"
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        }),
        label="Last Name"
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        label="Email Address"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'gst_number', 'pan_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields styled with form-control class
        for field_name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                field.widget.attrs = {}
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email.lower()

    def clean_pan_number(self):
        """Validate PAN format: 5 letters + 4 digits + 1 letter."""
        pan = self.cleaned_data.get('pan_number', '').upper().strip()

        if pan:
            # PAN pattern: ABCDE1234F (5 letters, 4 digits, 1 letter)
            pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
            if not pan_pattern.match(pan):
                raise ValidationError(
                    'Invalid PAN format. Must be 10 characters: '
                    '5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)'
                )
        return pan

    def clean_gst_number(self):
        """Validate GST format: 15 alphanumeric characters."""
        gst = self.cleaned_data.get('gst_number', '').upper().strip()

        if gst:
            # GST pattern: 22AAAAA0000A1Z5 (15 characters)
            gst_pattern = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$')
            if not gst_pattern.match(gst):
                raise ValidationError(
                    'Invalid GST format. Must be 15 characters (e.g., 22AAAAA0000A1Z5)'
                )
        return gst

    def clean_phone_number(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone_number', '').strip()

        if phone:
            # Remove spaces, dashes, parentheses
            phone_clean = re.sub(r'[\s\-\(\)]', '', phone)

            # Validate format: +91 followed by 10 digits, or just 10 digits
            phone_pattern = re.compile(r'^(\+?[0-9]{1,4})?[0-9]{10}$')
            if not phone_pattern.match(phone_clean):
                raise ValidationError(
                    'Invalid mobile number. Must be 10 digits '
                    '(optionally with country code like +91)'
                )
            return phone_clean
        return phone

    def clean_password(self):
        """Validate password strength."""
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            if not any(char.isalpha() for char in password):
                raise ValidationError('Password must contain at least one letter.')
            if not any(char.isdigit() for char in password):
                raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        """Validate password confirmation."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        return cleaned_data

    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Set default role for new registrations
        user.role = 'VIEWER'
        user.is_active = True
        if commit:
            user.save()
        return user
