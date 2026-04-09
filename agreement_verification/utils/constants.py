"""Constants for Agreement Verification Application."""

# Agreement Status
AGREEMENT_STATUS_CHOICES = [
    ('DRAFT', 'Draft'),
    ('SUBMITTED', 'Submitted'),
    ('UNDER_REVIEW', 'Under Review'),
    ('VERIFIED', 'Verified'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

# Invoice Status
INVOICE_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('PROCESSING', 'Processing'),
    ('VERIFIED', 'Verified'),
    ('DISCREPANCY', 'Discrepancy Found'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

# User Roles
ROLE_CHOICES = [
    ('ADMIN', 'Administrator'),
    ('VERIFIER', 'Verifier'),
    ('SUBMITTER', 'Submitter'),
    ('VIEWER', 'Viewer'),
]

# Verification Status
VERIFICATION_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('IN_PROGRESS', 'In Progress'),
    ('COMPLETED', 'Completed'),
]

# Verification Result
VERIFICATION_RESULT_CHOICES = [
    ('PASSED', 'Passed'),
    ('FAILED', 'Failed'),
    ('WARNING', 'Warning'),
]

# Discrepancy Types
DISCREPANCY_TYPE_CHOICES = [
    ('RATE_MISMATCH', 'Rate Mismatch'),
    ('QUANTITY_MISMATCH', 'Quantity Mismatch'),
    ('CALCULATION_ERROR', 'Calculation Error'),
    ('TOLERANCE_EXCEEDED', 'Tolerance Exceeded'),
]
