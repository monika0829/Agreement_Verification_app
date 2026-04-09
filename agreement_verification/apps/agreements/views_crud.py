"""
CRUD Views for Agreement app with proper form handling and business logic.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from datetime import datetime, timedelta
import json

try:
    from apps.agreements.models import Vendor, Agreement, RateConfiguration, Invoice, InvoiceDiscrepancy
    from apps.agreements.forms import (
        VendorForm, AgreementForm, RateConfigurationForm, InvoiceForm,
        InvoiceVerificationForm, InvoiceDiscrepancyForm, ApprovalActionForm, AgreementStatusForm
    )
    from apps.verification.models import VerificationRequest, VerificationCheck
except ImportError:
    from .models import Vendor, Agreement, RateConfiguration, Invoice, InvoiceDiscrepancy
    from .forms import (
        VendorForm, AgreementForm, RateConfigurationForm, InvoiceForm,
        InvoiceVerificationForm, InvoiceDiscrepancyForm, ApprovalActionForm, AgreementStatusForm
    )
    from apps.verification.models import VerificationRequest, VerificationCheck

from services.verification_service import VerificationService
from services.compliance_service import ComplianceService


@login_required
def dashboard(request):
    """Enhanced dashboard with statistics and metrics."""
    user = request.user

    # Get statistics
    total_vendors = Vendor.objects.filter(is_active=True).count()
    total_agreements = Agreement.objects.count()
    active_agreements = Agreement.objects.filter(status='ACTIVE').count()
    pending_agreements = Agreement.objects.filter(status='PENDING_APPROVAL').count()
    total_invoices = Invoice.objects.count()
    pending_invoices = Invoice.objects.filter(status='PENDING').count()
    verified_invoices = Invoice.objects.filter(status='VERIFIED').count()

    # Recent activity
    recent_agreements = Agreement.objects.select_related('vendor').order_by('-created_at')[:5]
    recent_invoices = Invoice.objects.select_related('vendor').order_by('-created_at')[:5]
    pending_approvals = Agreement.objects.filter(
        status='PENDING_APPROVAL'
    ).select_related('vendor', 'created_by')[:5]

    # Invoice status breakdown
    invoice_status_counts = dict(
        Invoice.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )
    invoice_status_labels = list(invoice_status_counts.keys())
    invoice_status_data = list(invoice_status_counts.values())

    # Agreement status breakdown
    agreement_status_counts = dict(
        Agreement.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )
    agreement_status_labels = list(agreement_status_counts.keys())
    agreement_status_data = list(agreement_status_counts.values())

    # Financial summary
    total_invoice_amount = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_invoice_amount = Invoice.objects.filter(
        status='PENDING'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Upcoming renewals (expiring in 30 days)
    upcoming_renewals = Agreement.objects.filter(
        status='ACTIVE',
        agreement_end_date__lte=timezone.now().date() + timedelta(days=30)
    ).select_related('vendor')

    # Discrepancy summary
    open_discrepancies = InvoiceDiscrepancy.objects.filter(is_resolved=False).count()
    total_discrepancies = InvoiceDiscrepancy.objects.count()

    context = {
        'page_title': 'Dashboard',
        'total_vendors': total_vendors,
        'total_agreements': total_agreements,
        'active_agreements': active_agreements,
        'pending_agreements': pending_agreements,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'verified_invoices': verified_invoices,
        'recent_agreements': recent_agreements,
        'recent_invoices': recent_invoices,
        'pending_approvals': pending_approvals,
        'invoice_status_counts': invoice_status_counts,
        'agreement_status_counts': agreement_status_counts,
        'invoice_status_labels': invoice_status_labels,
        'invoice_status_data': invoice_status_data,
        'agreement_status_labels': agreement_status_labels,
        'agreement_status_data': agreement_status_data,
        'total_invoice_amount': total_invoice_amount,
        'pending_invoice_amount': pending_invoice_amount,
        'upcoming_renewals': upcoming_renewals,
        'open_discrepancies': open_discrepancies,
        'total_discrepancies': total_discrepancies,
    }
    return render(request, 'agreements/dashboard.html', context)


# ==================== VENDOR CRUD VIEWS ====================

@login_required
def vendor_list(request):
    """List all vendors with search and filtering."""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    city_filter = request.GET.get('city', '')

    vendors = Vendor.objects.all()

    if search_query:
        vendors = vendors.filter(
            Q(name__icontains=search_query) |
            Q(vendor_code__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if status_filter == 'active':
        vendors = vendors.filter(is_active=True)
    elif status_filter == 'inactive':
        vendors = vendors.filter(is_active=False)

    if city_filter:
        vendors = vendors.filter(city__icontains=city_filter)

    # Get unique cities for filter
    cities = Vendor.objects.values_list('city', flat=True).distinct().order_by('city')

    # Pagination
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Vendors',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'city_filter': city_filter,
        'cities': cities,
    }
    return render(request, 'agreements/vendor_list.html', context)


@login_required
def vendor_create(request):
    """Create a new vendor."""
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" created successfully.')
            return redirect('agreements:vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm()

    context = {
        'page_title': 'Create Vendor',
        'form': form,
    }
    return render(request, 'agreements/vendor_form.html', context)


@login_required
def vendor_detail(request, pk):
    """View vendor details with related agreements and invoices."""
    vendor = get_object_or_404(Vendor, pk=pk)

    # Get related agreements
    agreements = vendor.agreements.select_related('account_manager').order_by('-created_at')[:10]

    # Get related invoices
    invoices = vendor.invoices.select_related('agreement').order_by('-invoice_date')[:10]

    # Statistics
    total_agreements = vendor.agreements.count()
    active_agreements = vendor.agreements.filter(status='ACTIVE').count()
    total_invoices_count = vendor.invoices.count()
    total_invoice_amount = vendor.invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    context = {
        'page_title': f'Vendor - {vendor.name}',
        'vendor': vendor,
        'agreements': agreements,
        'invoices': invoices,
        'total_agreements': total_agreements,
        'active_agreements': active_agreements,
        'total_invoices_count': total_invoices_count,
        'total_invoice_amount': total_invoice_amount,
    }
    return render(request, 'agreements/vendor_detail.html', context)


@login_required
def vendor_update(request, pk):
    """Update an existing vendor."""
    vendor = get_object_or_404(Vendor, pk=pk)

    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vendor "{vendor.name}" updated successfully.')
            return redirect('agreements:vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm(instance=vendor)

    context = {
        'page_title': f'Edit Vendor - {vendor.name}',
        'form': form,
        'vendor': vendor,
    }
    return render(request, 'agreements/vendor_form.html', context)


@login_required
def vendor_delete(request, pk):
    """Delete a vendor (soft delete by deactivating)."""
    vendor = get_object_or_404(Vendor, pk=pk)

    if request.method == 'POST':
        vendor.is_active = False
        vendor.save()
        messages.success(request, f'Vendor "{vendor.name}" has been deactivated.')
        return redirect('agreements:vendor_list')

    context = {
        'page_title': f'Delete Vendor - {vendor.name}',
        'vendor': vendor,
    }
    return render(request, 'agreements/vendor_confirm_delete.html', context)


# ==================== AGREEMENT CRUD VIEWS ====================

@login_required
def agreement_list(request):
    """List all agreements with search and filtering."""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    vendor_filter = request.GET.get('vendor', '')
    type_filter = request.GET.get('type', '')

    agreements = Agreement.objects.select_related('vendor', 'account_manager').all()

    if search_query:
        agreements = agreements.filter(
            Q(agreement_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(vendor__name__icontains=search_query)
        )

    if status_filter:
        agreements = agreements.filter(status=status_filter)

    if vendor_filter:
        agreements = agreements.filter(vendor_id=vendor_filter)

    if type_filter:
        agreements = agreements.filter(agreement_type=type_filter)

    # Get filter options
    vendors = Vendor.objects.filter(is_active=True).order_by('name')

    # Pagination
    paginator = Paginator(agreements, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Agreements',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'vendor_filter': vendor_filter,
        'type_filter': type_filter,
        'vendors': vendors,
        'status_choices': Agreement.STATUS_CHOICES if hasattr(Agreement, 'STATUS_CHOICES') else [],
    }
    return render(request, 'agreements/agreement_list.html', context)


@login_required
def agreement_create(request):
    """Create a new agreement."""
    if request.method == 'POST':
        form = AgreementForm(request.POST, request.FILES)
        if form.is_valid():
            agreement = form.save(commit=False)
            agreement.created_by = request.user
            agreement.save()
            messages.success(request, f'Agreement "{agreement.agreement_number}" created successfully.')
            return redirect('agreements:agreement_detail', pk=agreement.pk)
    else:
        form = AgreementForm()

    context = {
        'page_title': 'Create Agreement',
        'form': form,
    }
    return render(request, 'agreements/agreement_form.html', context)


@login_required
def agreement_detail(request, pk):
    """View agreement details with rates and invoices."""
    agreement = get_object_or_404(Agreement, pk=pk)

    # Get rate configurations
    rates = agreement.rates.all().order_by('rate_code')

    # Get related invoices
    invoices = agreement.invoices.select_related('vendor').order_by('-invoice_date')[:10]

    # Calculate statistics
    total_rates = rates.count()
    active_rates = rates.filter(is_active=True).count()
    total_invoices_count = agreement.invoices.count()

    # Check if agreement is expiring soon
    days_until_expiry = None
    if agreement.agreement_end_date:
        days_until_expiry = (agreement.agreement_end_date - timezone.now().date()).days

    context = {
        'page_title': f'Agreement - {agreement.agreement_number}',
        'agreement': agreement,
        'rates': rates,
        'invoices': invoices,
        'total_rates': total_rates,
        'active_rates': active_rates,
        'total_invoices_count': total_invoices_count,
        'days_until_expiry': days_until_expiry,
    }
    return render(request, 'agreements/agreement_detail.html', context)


@login_required
def agreement_update(request, pk):
    """Update an existing agreement."""
    agreement = get_object_or_404(Agreement, pk=pk)

    if request.method == 'POST':
        form = AgreementForm(request.POST, request.FILES, instance=agreement)
        if form.is_valid():
            form.save()
            messages.success(request, f'Agreement "{agreement.agreement_number}" updated successfully.')
            return redirect('agreements:agreement_detail', pk=agreement.pk)
    else:
        form = AgreementForm(instance=agreement)

    context = {
        'page_title': f'Edit Agreement - {agreement.agreement_number}',
        'form': form,
        'agreement': agreement,
    }
    return render(request, 'agreements/agreement_form.html', context)


@login_required
def agreement_change_status(request, pk):
    """Change agreement status."""
    agreement = get_object_or_404(Agreement, pk=pk)

    if request.method == 'POST':
        form = AgreementStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            reason = form.cleaned_data.get('reason', '')

            agreement.status = new_status

            if new_status == 'PENDING_APPROVAL':
                agreement.submitted_at = timezone.now()
                messages.success(request, 'Agreement submitted for approval.')
            elif new_status == 'ACTIVE':
                agreement.approved_at = timezone.now()
                agreement.approved_by = request.user
                messages.success(request, 'Agreement activated.')
            elif new_status == 'DRAFT':
                messages.info(request, 'Agreement returned to draft.')

            agreement.rejection_reason = reason if new_status in ['REJECTED', 'TERMINATED'] else ''
            agreement.save()

            return redirect('agreements:agreement_detail', pk=agreement.pk)
    else:
        form = AgreementStatusForm(initial={'status': agreement.status})

    context = {
        'page_title': f'Change Status - {agreement.agreement_number}',
        'form': form,
        'agreement': agreement,
    }
    return render(request, 'agreements/agreement_status.html', context)


# ==================== RATE CONFIGURATION VIEWS ====================

@login_required
def rate_create(request, agreement_pk):
    """Create a new rate configuration for an agreement."""
    agreement = get_object_or_404(Agreement, pk=agreement_pk)

    if request.method == 'POST':
        form = RateConfigurationForm(request.POST)
        if form.is_valid():
            rate = form.save(commit=False)
            rate.agreement = agreement
            rate.save()
            messages.success(request, f'Rate "{rate.rate_code}" created successfully.')
            return redirect('agreements:agreement_detail', pk=agreement.pk)
    else:
        form = RateConfigurationForm()

    context = {
        'page_title': f'Add Rate - {agreement.agreement_number}',
        'form': form,
        'agreement': agreement,
    }
    return render(request, 'agreements/rate_form.html', context)


@login_required
def rate_update(request, pk):
    """Update an existing rate configuration."""
    rate = get_object_or_404(RateConfiguration, pk=pk)

    if request.method == 'POST':
        form = RateConfigurationForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rate "{rate.rate_code}" updated successfully.')
            return redirect('agreements:agreement_detail', pk=rate.agreement.pk)
    else:
        form = RateConfigurationForm(instance=rate)

    context = {
        'page_title': f'Edit Rate - {rate.rate_code}',
        'form': form,
        'rate': rate,
    }
    return render(request, 'agreements/rate_form.html', context)


@login_required
def rate_delete(request, pk):
    """Delete a rate configuration."""
    rate = get_object_or_404(RateConfiguration, pk=pk)
    agreement_pk = rate.agreement.pk

    if request.method == 'POST':
        rate.delete()
        messages.success(request, f'Rate "{rate.rate_code}" deleted successfully.')
        return redirect('agreements:agreement_detail', pk=agreement_pk)

    context = {
        'page_title': f'Delete Rate - {rate.rate_code}',
        'rate': rate,
    }
    return render(request, 'agreements/rate_confirm_delete.html', context)


# ==================== INVOICE VIEWS ====================

@login_required
def invoice_list(request):
    """List all invoices with search and filtering."""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    vendor_filter = request.GET.get('vendor', '')

    invoices = Invoice.objects.select_related('vendor', 'agreement', 'verified_by').all()

    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(vendor__name__icontains=search_query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    if vendor_filter:
        invoices = invoices.filter(vendor_id=vendor_filter)

    # Get filter options
    vendors = Vendor.objects.filter(is_active=True).order_by('name')

    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Invoices',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'vendor_filter': vendor_filter,
        'vendors': vendors,
    }
    return render(request, 'agreements/invoice_list.html', context)


@login_required
def invoice_create(request):
    """Create/upload a new invoice."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.status = 'PENDING'
            invoice.save()
            messages.success(request, f'Invoice "{invoice.invoice_number}" uploaded successfully.')
            return redirect('agreements:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()

    context = {
        'page_title': 'Upload Invoice',
        'form': form,
    }
    return render(request, 'agreements/invoice_form.html', context)


@login_required
def invoice_detail(request, pk):
    """View invoice details with discrepancies and verification status."""
    invoice = get_object_or_404(Invoice, pk=pk)

    # Get discrepancies
    discrepancies = invoice.discrepancies.all().order_by('-created_at')

    # Get verification requests
    verification_requests = invoice.verification_requests.all().order_by('-created_at')

    # Calculate totals
    total_discrepancies = discrepancies.count()
    unresolved_discrepancies = discrepancies.filter(is_resolved=False).count()

    context = {
        'page_title': f'Invoice - {invoice.invoice_number}',
        'invoice': invoice,
        'discrepancies': discrepancies,
        'verification_requests': verification_requests,
        'total_discrepancies': total_discrepancies,
        'unresolved_discrepancies': unresolved_discrepancies,
    }
    return render(request, 'agreements/invoice_detail.html', context)


@login_required
def invoice_verify(request, pk):
    """Verify an invoice."""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        form = InvoiceVerificationForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            notes = form.cleaned_data.get('verification_notes', '')

            # Run verification if approving
            if action == 'approve':
                result = VerificationService.verify_invoice(invoice.pk)
                invoice.status = 'VERIFIED'
                invoice.verified_at = timezone.now()
                invoice.verified_by = request.user
                invoice.verification_notes = notes
                invoice.save()

                if result['discrepancies_found']:
                    messages.warning(
                        request,
                        f'Invoice verified with {len(result["discrepancies"])} discrepancies. '
                        f'Please review before final approval.'
                    )
                else:
                    messages.success(request, 'Invoice verified successfully with no discrepancies.')

            elif action == 'reject':
                invoice.status = 'REJECTED'
                invoice.rejection_reason = form.cleaned_data.get('rejection_reason', notes)
                invoice.save()
                messages.success(request, 'Invoice rejected.')

            else:  # request_info
                invoice.status = 'PENDING'
                invoice.verification_notes = notes
                invoice.save()
                messages.info(request, 'Request for more information sent.')

            return redirect('agreements:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceVerificationForm()

    # Run preliminary verification check
    verification_result = VerificationService.verify_invoice(invoice.pk, dry_run=True)

    context = {
        'page_title': f'Verify Invoice - {invoice.invoice_number}',
        'form': form,
        'invoice': invoice,
        'verification_result': verification_result,
    }
    return render(request, 'agreements/invoice_verify.html', context)


@login_required
def invoice_approve(request, pk):
    """Approve a verified invoice."""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        invoice.status = 'APPROVED'
        invoice.approved_at = timezone.now()
        invoice.approved_by = request.user
        invoice.save()

        messages.success(request, f'Invoice "{invoice.invoice_number}" approved successfully.')
        return redirect('agreements:invoice_detail', pk=invoice.pk)

    context = {
        'page_title': f'Approve Invoice - {invoice.invoice_number}',
        'invoice': invoice,
    }
    return render(request, 'agreements/invoice_approve.html', context)


# ==================== DISCREPANCY VIEWS ====================

@login_required
def discrepancy_resolve(request, pk):
    """Resolve a discrepancy."""
    discrepancy = get_object_or_404(InvoiceDiscrepancy, pk=pk)

    if request.method == 'POST':
        form = InvoiceDiscrepancyForm(request.POST, instance=discrepancy)
        if form.is_valid():
            discrepancy = form.save(commit=False)
            if discrepancy.is_resolved:
                discrepancy.resolved_at = timezone.now()
                discrepancy.resolved_by = request.user
            discrepancy.save()
            messages.success(request, 'Discrepancy resolved successfully.')
            return redirect('agreements:invoice_detail', pk=discrepancy.invoice.pk)
    else:
        form = InvoiceDiscrepancyForm(instance=discrepancy)

    context = {
        'page_title': 'Resolve Discrepancy',
        'form': form,
        'discrepancy': discrepancy,
    }
    return render(request, 'agreements/discrepancy_resolve.html', context)


# ==================== VERIFICATION & APPROVAL VIEWS ====================

@login_required
def verification_list(request):
    """List all verification requests."""
    verifications = VerificationRequest.objects.select_related(
        'created_by', 'assigned_to', 'agreement', 'invoice'
    ).order_by('-created_at')

    # Filtering
    status_filter = request.GET.get('status', '')
    if status_filter:
        verifications = verifications.filter(status=status_filter)

    # Get user's assigned verifications
    my_verifications = verifications.filter(assigned_to=request.user)

    context = {
        'page_title': 'Verifications',
        'verifications': verifications,
        'my_verifications': my_verifications,
        'status_filter': status_filter,
    }
    return render(request, 'agreements/verification_list.html', context)


@login_required
def verification_detail(request, pk):
    """View verification request details."""
    verification = get_object_or_404(
        VerificationRequest.objects.select_related(),
        pk=pk
    )

    checks = verification.checks.all().order_by('display_order')

    context = {
        'page_title': f'Verification - {verification.reference_number}',
        'verification': verification,
        'checks': checks,
    }
    return render(request, 'agreements/verification_detail.html', context)
