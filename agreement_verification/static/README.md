# Agreement Verification Application - Frontend

A modern, responsive HTML/CSS/JavaScript frontend for the Agreement Verification Application.

## Features

- 🔐 **JWT Authentication** - Secure login with token management
- 📊 **Dashboard** - Overview with statistics and quick actions
- 🏢 **Vendor Management** - Full CRUD operations for vendors
- 📄 **Agreement Management** - Create and manage vendor agreements
- 🧾 **Invoice Processing** - Upload and verify invoices against agreements
- ✓ **Verification Workflow** - Track and manage verification requests
- 🔍 **Compliance Dashboard** - View compliance rules and status

## Quick Start

### Option 1: Simple HTTP Server

```bash
cd /workspace/frontend-static
python3 -m http.server 8080
```

Then access at: http://localhost:8080

### Option 2: Serve via Django (Production)

Add to Django `urls.py`:

```python
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static('/frontend/', document_root='/workspace/frontend-static')
```

Place the `frontend-static` folder in your Django project's templates directory.

## API Configuration

The frontend connects to the Django backend at:

```
https://ds537u232p80.drytis.ai/api/v1
```

For local development, edit `index.html` and change:

```javascript
const API_BASE = 'https://ds537u232p80.drytis.ai/api/v1';
// to:
const API_BASE = 'http://localhost:8000/api/v1';
```

## Default Credentials

- **Email**: admin@example.com
- **Password**: Admin123!

## Project Structure

```
frontend-static/
├── index.html          # Main application (SPA)
├── css/
│   └── style.css      # All styles
├── js/                # (reserved for future JS modules)
└── pages/             # (reserved for future page modules)
```

## Pages & Features

### 1. Login Page (`/`)
- Email/password authentication
- JWT token storage
- Auto-redirect if logged in

### 2. Dashboard (`/dashboard`)
- Statistics cards (vendors, agreements, invoices, verifications)
- Quick action buttons
- Recent activity overview

### 3. Vendors (`/vendors`)
- View all vendors in card grid
- Add new vendor modal
- Display vendor details
- Active/Inactive status

### 4. Agreements (`/agreements`)
- List all agreements in table
- Filter by status
- View agreement details
- Create new agreement (coming soon)

### 5. Invoices (`/invoices`)
- List all invoices
- Upload invoice modal
- Verify invoice (checks against agreement rates)
- Approve verified invoices
- Status tracking

### 6. Verifications (`/verifications`)
- View verification requests
- Track verification status
- Display verification details

## API Integration

The frontend uses the following API endpoints:

- `POST /api/v1/auth/login/` - Authentication
- `GET /api/v1/vendors/` - List vendors
- `POST /api/v1/vendors/` - Create vendor
- `GET /api/v1/agreements/` - List agreements
- `GET /api/v1/invoices/` - List invoices
- `POST /api/v1/invoices/{id}/verify/` - Verify invoice
- `POST /api/v1/invoices/{id}/approve/` - Approve invoice
- `GET /api/v1/verifications/` - List verifications

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development

To modify the frontend:

1. Edit `index.html` for structure changes
2. Edit `css/style.css` for styling
3. No build step required - pure HTML/CSS/JS

## Deployment

### Django Static Files

Copy to Django static files:

```bash
cp -r frontend-static /workspace/agreement_verification/static/
```

Add to Django settings:

```python
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### Standalone Server

Any HTTP server works:

```bash
# Python
python3 -m http.server 8080

# Node.js (npx)
npx serve frontend-static

# PHP
php -S localhost:8080
```

## Features Implemented

✅ Single Page Application (SPA)
✅ JWT Authentication with auto-refresh
✅ Responsive design (mobile-friendly)
✅ Dashboard with statistics
✅ Vendor CRUD operations
✅ Agreement listing
✅ Invoice upload and verification
✅ Status tracking
✅ Modal dialogs for forms
✅ Real-time API integration
✅ Error handling
✅ Loading states

## Security

- JWT tokens stored in localStorage
- Automatic token refresh on 401 errors
- Secure HTTPS in production
- CORS enabled for API communication

## Support

For issues or questions, refer to the backend API documentation at `/api/docs/`
