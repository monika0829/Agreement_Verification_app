# Agreement Verification Application

A comprehensive Django REST API for managing vendor agreements, invoice verification, and compliance checking.

## Project Structure

```
agreement_verification/
├── config/                 # Django settings and configuration
├── apps/
│   ├── users/            # User management with custom User model
│   ├── agreements/       # Vendor, Agreement, Rate, Invoice models
│   ├── verification/     # Verification workflow and approval
│   ├── compliance/       # Compliance rule engine
│   ├── serializers.py    # All DRF serializers
│   ├── views.py          # All DRF viewsets
│   └── api_urls.py       # API v1 URL routing
├── services/             # Business logic layer
│   ├── verification_service.py  # Invoice verification logic
│   └── compliance_service.py    # Rule engine execution
├── utils/                # Shared utilities
│   ├── constants.py      # Status/role choices
│   ├── validators.py     # Custom validators
│   ├── helpers.py        # Helper functions
│   └── pagination.py     # Pagination classes
├── media/                # Uploaded files
├── static/               # Static files
└── db.sqlite3            # SQLite database (switch to MySQL in production)

```

## Models Implemented

### Users App
- **User**: Custom user model with email authentication and role-based access

### Agreements App
- **Vendor**: Vendor information management
- **Agreement**: Vendor agreements with status tracking
- **RateConfiguration**: Freight rates with tolerance settings
- **Invoice**: Invoice processing and verification
- **InvoiceDiscrepancy**: Discrepancy tracking

### Verification App
- **VerificationRequest**: Verification workflow management
- **VerificationCheck**: Individual verification checks
- **ApprovalWorkflow**: Approval workflow configuration
- **ApprovalProcess**: Active approval processes

### Compliance App
- **ComplianceRule**: Rule definitions
- **ComplianceCheck**: Rule execution results
- **ComplianceReport**: Aggregated compliance reports

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - Get JWT token
- `POST /api/v1/auth/refresh/` - Refresh JWT token

### Core Resources
- `GET/POST /api/v1/vendors/` - Manage vendors
- `GET/POST /api/v1/agreements/` - Manage agreements
- `GET/POST /api/v1/rates/` - Manage rate configurations
- `GET/POST /api/v1/invoices/` - Manage invoices
- `GET/POST /api/v1/invoice-discrepancies/` - Manage discrepancies
- `GET/POST /api/v1/verifications/` - Verification requests
- `GET/POST /api/v1/compliance-rules/` - Compliance rules

### Actions
- `POST /api/v1/agreements/{id}/submit/` - Submit agreement
- `POST /api/v1/agreements/{id}/approve/` - Approve agreement
- `POST /api/v1/invoices/{id}/verify/` - Verify invoice
- `POST /api/v1/invoices/{id}/approve/` - Approve invoice
- `POST /api/v1/invoice-discrepancies/{id}/resolve/` - Resolve discrepancy
- `POST /api/v1/verifications/{id}/assign/` - Assign verification
- `POST /api/v1/verifications/{id}/start/` - Start verification
- `POST /api/v1/verifications/{id}/complete/` - Complete verification

## Default Credentials

- **Email**: admin@example.com
- **Password**: Admin123!

## Running the Application

### Development
```bash
cd /workspace/agreement_verification
source /workspace/venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Production with Gunicorn
```bash
source /workspace/venv/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Verification Engine

The verification engine checks invoices against agreement rates:

1. **Rate Matching**: Finds applicable rates based on line items
2. **Tolerance Check**: Validates amounts are within tolerance percentage
3. **Discrepancy Creation**: Records any mismatches
4. **Status Update**: Updates invoice status (VERIFIED/DISCREPANCY)

## Services Layer

- **VerificationService**: Invoice verification logic with Excel processing
- **ComplianceService**: Rule engine execution and compliance checking

## Database Schema

All migrations have been applied. To switch to MySQL:

1. Update `DATABASES` in `config/settings.py`
2. Install `mysqlclient` or use `pymysql`
3. Run migrations: `python manage.py migrate`

## Status

✅ Project Structure Complete
✅ Models Implemented
✅ Serializers Created
✅ Views & Viewsets Complete
✅ Services Layer Complete
✅ API Endpoints Working
✅ Authentication Working
✅ Database Migrated
✅ Root URL Configured
