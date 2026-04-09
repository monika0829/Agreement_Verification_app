# Agreement Verification Application - Complete Implementation Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Complete Folder Structure](#complete-folder-structure)
3. [Database Design & ER Diagram](#database-design--er-diagram)
4. [API Endpoints Documentation](#api-endpoints-documentation)
5. [Verification Engine](#verification-engine)
6. [Approval Workflow Logic](#approval-workflow-logic)
7. [Excel Processing](#excel-processing)
8. [Performance Considerations](#performance-considerations)
9. [Sample Test Data](#sample-test-data)
10. [Deployment with Caddy](#deployment-with-caddy)

---

## 1. Project Overview

**Application Name:** Agreement Verification Application  
**Project ID:** 537  
**Stack:** Django 4.2 + Django REST Framework + React  
**Database:** SQLite (development) / MySQL (production)  

### Purpose
A comprehensive system for managing vendor agreements, verifying freight invoices, and tracking compliance through automated workflows.

### Key Features
- ✅ Vendor Management (CRUD operations)
- ✅ Agreement Lifecycle Management
- ✅ Rate Configuration for Freight/Services
- ✅ Invoice Upload & Verification Engine
- ✅ Compliance Rule Engine
- ✅ Approval Workflow System
- ✅ Dashboard & Analytics

---

## 2. Complete Folder Structure

```
/workspace/
├── agreement_verification/          # Django Backend
│   ├── config/                      # Django configuration
│   │   ├── settings.py             # Main settings
│   │   ├── urls.py                 # Root URL configuration
│   │   └── wsgi.py                 # WSGI application
│   ├── apps/
│   │   ├── users/                  # User management app
│   │   │   ├── models/
│   │   │   │   └── user.py         # Custom User model
│   │   │   └── apps.py
│   │   ├── agreements/             # Core agreements app
│   │   │   ├── models/
│   │   │   │   └── vendor.py       # Vendor, Agreement, Rate, Invoice models
│   │   │   └── apps.py
│   │   ├── verification/           # Verification workflow app
│   │   │   ├── models/
│   │   │   │   └── workflow.py     # VerificationRequest, ApprovalWorkflow models
│   │   │   └── apps.py
│   │   ├── compliance/             # Compliance rules app
│   │   │   ├── models/
│   │   │   │   └── rules.py        # ComplianceRule, ComplianceCheck models
│   │   │   └── apps.py
│   │   ├── serializers.py          # All DRF serializers
│   │   ├── views.py                # All DRF viewsets
│   │   └── api_urls.py             # API v1 URL routing
│   ├── services/                   # Business logic layer
│   │   ├── verification_service.py # Invoice verification logic
│   │   └── compliance_service.py   # Rule engine execution
│   ├── utils/                      # Shared utilities
│   │   ├── constants.py            # Status/role choices
│   │   ├── validators.py           # Custom validators
│   │   ├── helpers.py              # Helper functions
│   │   └── pagination.py           # Pagination classes
│   ├── media/                      # Uploaded files
│   ├── static/                     # Static files
│   ├── manage.py                   # Django management script
│   └── db.sqlite3                  # SQLite database
├── frontend/                       # React Frontend
│   ├── public/
│   │   └── index.html              # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.js           # Main layout with sidebar
│   │   ├── pages/
│   │   │   ├── Login.js            # Login page
│   │   │   ├── Dashboard.js        # Dashboard
│   │   │   ├── Vendors.js          # Vendor management
│   │   │   ├── Agreements.js       # Agreement management
│   │   │   ├── Invoices.js         # Invoice management
│   │   │   ├── Verifications.js   # Verification management
│   │   │   └── Compliance.js       # Compliance dashboard
│   │   ├── services/
│   │   │   └── api.js              # API service layer
│   │   ├── styles/
│   │   │   ├── index.css          # Base styles
│   │   │   ├── Layout.css          # Layout styles
│   │   │   └── *.css              # Page-specific styles
│   │   ├── App.js                 # Main React component
│   │   └── index.js               # React entry point
│   └── package.json                # Node.js dependencies
├── venv/                          # Python virtual environment
├── logs/                          # Application logs
└── README.md                      # Project documentation
```

---

## 3. Database Design & ER Diagram

### Database Tables

#### 1. users_user
```
- id (PK)
- email (unique)
- first_name
- last_name
- password (hashed)
- role (choices: ADMIN, VERIFIER, SUBMITTER, VIEWER)
- is_staff
- is_active
- date_joined
```

#### 2. vendors
```
- id (PK)
- vendor_code (unique)
- name
- email
- phone
- address
- city
- state
- country
- tax_id
- is_active
- created_at
- updated_at
```

#### 3. agreements
```
- id (PK)
- agreement_number (unique)
- vendor_id (FK → vendors)
- agreement_type (VENDOR, FREIGHT, SERVICE)
- title
- description
- status (DRAFT, SUBMITTED, UNDER_REVIEW, VERIFIED, APPROVED, REJECTED)
- agreement_start_date
- agreement_end_date
- currency
- estimated_annual_value
- payment_terms
- account_manager_id (FK → users_user)
- approved_by_id (FK → users_user)
- created_at
- updated_at
```

#### 4. rate_configurations
```
- id (PK)
- agreement_id (FK → agreements)
- rate_code (unique with agreement)
- rate_name
- rate_type (FLAT_RATE, PER_MILE, PER_KG, PER_LB)
- rate
- currency
- origin
- destination
- service_level
- equipment_type
- effective_start_date
- effective_end_date
- tolerance_percentage
- is_active
```

#### 5. invoices
```
- id (PK)
- invoice_number (unique)
- vendor_id (FK → vendors)
- agreement_id (FK → agreements)
- invoice_date
- due_date
- currency
- subtotal_amount
- tax_amount
- total_amount
- amount_paid
- status (PENDING, PROCESSING, VERIFIED, DISCREPANCY, APPROVED, REJECTED)
- invoice_file (file upload)
- line_items (JSON)
- verified_by_id (FK → users_user)
- verified_at
- approved_by_id (FK → users_user)
- approved_at
```

#### 6. invoice_discrepancies
```
- id (PK)
- invoice_id (FK → invoices)
- rate_configuration_id (FK → rate_configurations)
- discrepancy_type (RATE_MISMATCH, QUANTITY_MISMATCH, CALCULATION_ERROR, TOLERANCE_EXCEEDED)
- description
- expected_value
- actual_value
- difference
- difference_percentage
- financial_impact
- is_resolved
- resolved_by_id (FK → users_user)
```

#### 7. verification_requests
```
- id (PK)
- reference_number (unique)
- request_type (AGREEMENT, INVOICE)
- agreement_id (FK → agreements)
- invoice_id (FK → invoices)
- title
- description
- status (PENDING, IN_PROGRESS, COMPLETED)
- result (PASSED, FAILED, WARNING)
- priority (LOW, MEDIUM, HIGH)
- assigned_to_id (FK → users_user)
- started_at
- completed_at
```

#### 8. approval_workflows
```
- id (PK)
- workflow_type
- workflow_name
- description
- is_active
- workflow_steps (JSON)
```

#### 9. approval_processes
```
- id (PK)
- workflow_id (FK → approval_workflows)
- entity_type
- entity_id
- reference_number
- title
- current_step
- status (IN_PROGRESS, APPROVED, REJECTED)
- requested_by_id (FK → users_user)
```

#### 10. compliance_rules
```
- id (PK)
- rule_code (unique)
- rule_name
- rule_description
- rule_type (VALIDATION, BUSINESS_LOGIC, CALCULATION)
- category (AGREEMENT, INVOICE, VENDOR)
- severity (LOW, MEDIUM, HIGH, CRITICAL)
- is_active
- rule_config (JSON)
- error_message
```

### ER Diagram

```
┌──────────────┐
│ users_user   │
└──────┬───────┘
       │
       ├──────────────────┐
       │                  │
┌──────▼───────┐  ┌──────▼──────────┐
│   vendors    │  │  agreements     │
└──────┬───────┘  └──────┬──────────┘
       │                │
       │         ┌──────┴──────────┐
       │         │ rate_configs   │
       │         └─────────────────┘
┌──────▼───────┐
│   invoices   │◄───────────────┐
└──────┬───────┘                │
       │                        │
┌──────▼─────────────┐          │
│invoice_discrepancies│          │
└─────────────────────┘          │
                                  │
                    ┌───────────▼───────────┐
                    │ verification_requests │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  approval_processes   │
                    └───────────────────────┘
```

---

## 4. API Endpoints Documentation

### Base URL
```
Local: http://localhost:8000/api/v1
```

### Authentication

#### POST /auth/login/
Authenticate and receive JWT token.

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "Admin123!"
}
```

**Response:**
```json
{
  "refresh": "eyJhbGc...",
  "access": "eyJhbGc..."
}
```

#### POST /auth/refresh/
Refresh access token.

**Request:**
```json
{
  "refresh": "token_here"
}
```

### Vendors

#### GET /vendors/
List all vendors.

**Query Parameters:**
- `is_active`: true/false
- `search`: search term

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "vendor_code": "VENDOR001",
      "name": "ABC Freight Co.",
      "email": "contact@abc.com",
      "phone": "+1-555-0100",
      "is_active": true
    }
  ]
}
```

#### POST /vendors/
Create new vendor.

#### PUT /vendors/{id}/
Update vendor.

#### DELETE /vendors/{id}/
Delete vendor.

### Agreements

#### GET /agreements/
List agreements with filtering.

**Query Parameters:**
- `vendor`: vendor_id
- `status`: DRAFT, SUBMITTED, APPROVED, etc.
- `agreement_type`: VENDOR, FREIGHT, SERVICE
- `search`: search term

#### POST /agreements/
Create new agreement.

**Request:**
```json
{
  "agreement_number": "AGR-2024-001",
  "vendor": 1,
  "agreement_type": "FREIGHT",
  "title": "West Coast Freight Agreement",
  "agreement_start_date": "2024-01-01",
  "agreement_end_date": "2024-12-31",
  "currency": "USD",
  "estimated_annual_value": 500000.00
}
```

#### POST /agreements/{id}/submit/
Submit agreement for review.

#### POST /agreements/{id}/approve/
Approve agreement.

### Rate Configurations

#### GET /rates/
List rate configurations.

**Query Parameters:**
- `agreement`: agreement_id
- `rate_type`: FLAT_RATE, PER_MILE, etc.
- `is_active`: true/false

#### POST /rates/
Create rate configuration.

**Request:**
```json
{
  "agreement": 1,
  "rate_code": "RATE-LAX-SFO",
  "rate_name": "Los Angeles to San Francisco",
  "rate_type": "PER_MILE",
  "rate": 2.50,
  "origin": "Los Angeles, CA",
  "destination": "San Francisco, CA",
  "tolerance_percentage": 5.00
}
```

### Invoices

#### GET /invoices/
List invoices.

**Query Parameters:**
- `vendor`: vendor_id
- `agreement`: agreement_id
- `status`: PENDING, VERIFIED, DISCREPANCY, APPROVED

#### POST /invoices/
Upload invoice.

**Request:** multipart/form-data
```
invoice_file: file
invoice_number: "INV-2024-001"
vendor: 1
agreement: 1
total_amount: 5000.00
line_items: [{"description": "Freight", "amount": 5000}]
```

#### POST /invoices/{id}/verify/
Verify invoice against agreement rates.

**Response:**
```json
{
  "status": "VERIFIED",
  "message": "Invoice verified",
  "result": {...}
}
```

#### POST /invoices/{id}/approve/
Approve verified invoice.

### Invoice Discrepancies

#### GET /invoice-discrepancies/
List discrepancies.

**Query Parameters:**
- `invoice`: invoice_id
- `discrepancy_type`: type
- `is_resolved`: true/false

#### POST /invoice-discrepancies/{id}/resolve/
Resolve discrepancy.

**Request:**
```json
{
  "notes": "Difference within acceptable range"
}
```

### Verification Requests

#### GET /verifications/
List verification requests.

#### POST /verifications/
Create verification request.

#### POST /verifications/{id}/assign/
Assign to user.

#### POST /verifications/{id}/start/
Start verification.

#### POST /verifications/{id}/complete/
Complete verification.

### Compliance

#### GET /compliance-rules/
List compliance rules.

---

## 5. Verification Engine

### Verification Service
Location: `/workspace/agreement_verification/services/verification_service.py`

### Verification Process Flow

```
1. Invoice Upload
   ↓
2. Extract Line Items (from JSON/Excel)
   ↓
3. Find Matching Rate Configuration
   - Match by: service_type, equipment_type, origin/destination
   ↓
4. Calculate Expected Cost
   - Based on rate_type and quantity/distance/weight
   ↓
5. Compare with Actual Invoice Amount
   ↓
6. Check Tolerance
   - if (difference / expected) <= tolerance_percentage:
       → VERIFIED
   - else:
       → DISCREPANCY (create InvoiceDiscrepancy record)
   ↓
7. Update Invoice Status
```

### Rate Calculation Logic

```python
class RateConfiguration:
    def calculate_cost(self, quantity=1, distance=0, weight=0):
        base_rate = float(self.rate)
        
        if self.rate_type == 'FLAT_RATE':
            return base_rate
        elif self.rate_type == 'PER_MILE':
            return base_rate * distance
        elif self.rate_type == 'PER_KG':
            return base_rate * weight
        elif self.rate_type == 'PER_LB':
            return base_rate * (weight * 2.20462)
        else:
            return base_rate * quantity
```

### Tolerance Checking

```python
def is_within_tolerance(expected: float, actual: float, tolerance_pct: float) -> bool:
    if expected == 0:
        return actual == 0
    
    difference = abs(expected - actual)
    tolerance_amount = (expected * tolerance_pct) / 100
    return difference <= tolerance_amount
```

### Example Verification

**Invoice Line Item:**
```json
{
  "line_number": "1",
  "description": "Freight from LAX to SFO",
  "quantity": 1,
  "distance": 380,
  "weight": 5000,
  "amount": 980.00
}
```

**Matching Rate:**
```json
{
  "rate_code": "LAX-SFO-PER-MILE",
  "rate_type": "PER_MILE",
  "rate": 2.50,
  "tolerance_percentage": 5.00
}
```

**Calculation:**
```
Expected: 2.50 × 380 = $950.00
Actual: $980.00
Difference: $30.00
Tolerance: 5% of $950 = $47.50

Since $30 < $47.50 → VERIFIED
```

---

## 6. Approval Workflow Logic

### Workflow Stages

```
┌──────────┐
│  DRAFT   │  Created by user
└────┬─────┘
     │
     ↓ (Submit)
┌──────────┐
│ SUBMITTED│  Pending review
└────┬─────┘
     │
     ↓ (Assign Reviewer)
┌──────────────┐
│ UNDER_REVIEW │  Being reviewed
└────┬─────────┘
     │
     ├─────────────┬──────────────┐
     ↓             ↓              ↓
┌─────────┐  ┌─────────┐  ┌────────┐
│VERIFIED │  │REJECTED │  │CANCEL  │
└────┬────┘  └─────────┘  └─────────┘
     │
     ↓ (Final Approval)
┌──────────┐
│ APPROVED │  Final state
└──────────┘
```

### Approval Process Model

```python
class ApprovalProcess:
    workflow = models.ForeignKey(ApprovalWorkflow)
    entity_type = models.CharField()  # 'Agreement', 'Invoice'
    entity_id = models.IntegerField()
    current_step = models.PositiveIntegerField(default=1)
    status = models.CharField()  # IN_PROGRESS, APPROVED, REJECTED
```

### State Transition Rules

```python
VALID_TRANSITIONS = {
    'DRAFT': ['SUBMITTED', 'CANCELLED'],
    'SUBMITTED': ['UNDER_REVIEW', 'REJECTED', 'CANCELLED'],
    'UNDER_REVIEW': ['VERIFIED', 'REJECTED', 'CANCELLED'],
    'VERIFIED': ['APPROVED', 'REJECTED'],
    'APPROVED': [],
    'REJECTED': ['SUBMITTED', 'CANCELLED'],
}
```

---

## 7. Excel Processing

### Supported File Types
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

### Excel Format Template

| Invoice Number | Invoice Date | Due Date | Total Amount | Line Number | Description | Quantity | Amount |
|----------------|-------------|----------|--------------|-------------|-------------|----------|---------|
| INV-2024-001  | 2024-01-15  | 2024-02-15| 5000.00      | 1           | Freight LAX-SFO| 1        | 4500.00|
| INV-2024-001  | 2024-01-15  | 2024-02-15| 5000.00      | 2           | Fuel Surcharge | 1        | 500.00 |

### Processing Code

```python
import pandas as pd

def process_excel_invoice(file_path: str) -> dict:
    df = pd.read_excel(file_path)
    
    invoice_data = {
        'invoice_number': str(df.iloc[0]['Invoice Number']),
        'invoice_date': pd.to_datetime(df.iloc[0]['Invoice Date']).date(),
        'total_amount': float(df.iloc[0]['Total Amount']),
        'line_items': []
    }
    
    for _, row in df.iterrows():
        invoice_data['line_items'].append({
            'line_number': str(row.get('Line Number')),
            'description': str(row.get('Description')),
            'quantity': float(row.get('Quantity', 1)),
            'amount': float(row.get('Amount', 0)),
        })
    
    return invoice_data
```

---

## 8. Performance Considerations

### Database Optimization

1. **Indexes Applied:**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['agreement_number']),
           models.Index(fields=['vendor']),
           models.Index(fields=['status']),
           models.Index(fields=['created_at']),
       ]
   ```

2. **Query Optimization:**
   ```python
   # Use select_related for ForeignKeys
   Agreement.objects.select_related('vendor', 'account_manager')
   
   # Use prefetch_related for ManyToMany
   agreement.agreement_set.prefetch_related('rates')
   
   # Only fetch needed fields
   Agreement.objects.only('id', 'agreement_number', 'title', 'status')
   ```

3. **Pagination:**
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardResultsSetPagination',
       'PAGE_SIZE': 20,
       'MAX_PAGE_SIZE': 100,
   }
   ```

### Caching Strategy

```python
from django.core.cache import cache

# Cache compliance rules (frequently accessed)
def get_active_rules():
    cache_key = 'compliance:rules:active'
    rules = cache.get(cache_key)
    if not rules:
        rules = ComplianceRule.objects.filter(is_active=True)
        cache.set(cache_key, rules, 3600)  # 1 hour
    return rules
```

### Async Processing for Heavy Tasks

```python
# For large Excel files, use Celery
from celery import shared_task

@shared_task
def process_large_invoice_async(invoice_id):
    # Processing logic here
    pass
```

### File Upload Optimization

```python
# Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

# Chunked reading for large files
import pandas as pd

df = pd.read_excel(file_path, chunksize=1000)
for chunk in df:
    process_chunk(chunk)
```

---

## 9. Sample Test Data

### Vendor Data

```sql
INSERT INTO vendors (vendor_code, name, email, phone, address, city, state, country, is_active)
VALUES 
('VEN001', 'ABC Freight Logistics', 'contact@abc.com', '+1-555-0100', '123 Main St', 'Los Angeles', 'CA', 'USA', true),
('VEN002', 'XYZ Shipping Co', 'info@xyz.com', '+1-555-0200', '456 Harbor Blvd', 'Long Beach', 'CA', 'USA', true);
```

### Agreement Data

```sql
INSERT INTO agreements (agreement_number, vendor_id, agreement_type, title, status, agreement_start_date, agreement_end_date, currency, estimated_annual_value)
VALUES
('AGR-2024-001', 1, 'FREIGHT', 'West Coast Freight Agreement 2024', 'APPROVED', '2024-01-01', '2024-12-31', 'USD', 500000.00);
```

### Rate Configuration

```sql
INSERT INTO rate_configurations (agreement_id, rate_code, rate_name, rate_type, rate, origin, destination, tolerance_percentage, is_active)
VALUES
(1, 'LAX-SFO-FLAT', 'LAX to SFO Flat Rate', 'FLAT_RATE', 1000.00, 'Los Angeles, CA', 'San Francisco, CA', 5.00, true),
(1, 'LAX-SFO-PER-MILE', 'LAX to SFO Per Mile', 'PER_MILE', 2.50, 'Los Angeles, CA', 'San Francisco, CA', 5.00, true);
```

### Example Invoice File

**File:** `invoice_template.xlsx`

| Column | Value |
|--------|-------|
| Invoice Number | INV-2024-001 |
| Invoice Date | 2024-01-15 |
| Due Date | 2024-02-15 |
| Line Number | 1 |
| Description | Freight Service: LAX to SFO |
| Quantity | 1 |
| Amount | 950.00 |

**Expected Verification Result:**
- Distance: ~380 miles
- Rate: $2.50/mile
- Expected: $950.00
- Tolerance: 5% ($47.50)
- Status: VERIFIED

---

## 10. Deployment with Caddy

### Caddy Configuration

Create Caddyfile at `/etc/caddy/Caddyfile`:

```

    # Static files
    handle /static/* {
        root * /workspace/agreement_verification/static
        file_server browse
    }
    
    # Media files
    handle /media/* {
        root * /workspace/agreement_verification/media
        file_server browse
    }
    
    # Health check endpoint
    handle /health {
        respond {"status":"healthy"}
    }
    
    # CORS headers
    header {
        Access-Control-Allow-Origin *
        Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
        Access-Control-Allow-Headers "Content-Type, Authorization"
    }
}
```

### Gunicorn Production Service

```bash
# Create systemd service
sudo nano /etc/systemd/system/agreement-verification.service
```

```ini
[Unit]
Description=Agreement Verification Application
After=network.target

[Service]
User=coder
Group=coder
WorkingDirectory=/workspace/agreement_verification
Environment="PATH=/workspace/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings"
ExecStart=/workspace/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

### Deploy Commands

```bash
# 1. Install dependencies
cd /workspace
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run migrations
cd agreement_verification
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Start service
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

# 6. Configure Caddy proxy
sudo systemctl reload caddy
```

### Verify Deployment


```

### Environment Variables

```bash
# .env file
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=agreement_verification
DATABASE_USER=root
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

---

## Default Credentials

**Admin User:**
- Email: `admin@example.com`
- Password: `Admin123!`

---

## Testing Checklist

- [ ] Login to admin panel
- [ ] Create vendor
- [ ] Create agreement with rates
- [ ] Upload invoice
- [ ] Verify invoice
- [ ] Check for discrepancies
- [ ] Create verification request
- [ ] Complete verification workflow
- [ ] View compliance dashboard
- [ ] Test approval workflow

---

## Support & Maintenance

**Logs Location:** `/workspace/logs/`  
**Database Backup:** Daily automated  
**Static Files:** `/workspace/agreement_verification/staticfiles/`  
**Media Files:** `/workspace/agreement_verification/media/`

**Restart Application:**
```bash
sudo systemctl restart agreement-verification
sudo systemctl reload caddy
```

**View Logs:**
```bash
tail -f /workspace/logs/django.log
```

---

*Implementation completed for Project ID 537*
