"""Custom validators."""
from django.core.exceptions import ValidationError

def validate_file_size(file, max_size=10*1024*1024):
    """Validate file size (max 10MB)."""
    if file.size > max_size:
        raise ValidationError(f'File size exceeds {max_size/(1024*1024)}MB')

def validate_file_extension(file, allowed_extensions=['.pdf', '.xlsx', '.xls']):
    """Validate file extension."""
    import os
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'File extension {ext} not allowed')
