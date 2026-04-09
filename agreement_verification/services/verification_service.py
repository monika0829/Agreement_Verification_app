"""Verification service for invoice and agreement verification."""
from django.db import transaction
from django.utils import timezone
from apps.agreements.models.vendor import Invoice, RateConfiguration, InvoiceDiscrepancy
from apps.verification.models.workflow import VerificationRequest, VerificationCheck
from utils.helpers import is_within_tolerance

class VerificationService:
    """Service for verification business logic."""

    @staticmethod
    @transaction.atomic
    def verify_invoice(invoice_id: int) -> dict:
        """Verify an invoice against its agreement rates."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return {'error': 'Invoice not found'}

        if not invoice.agreement:
            return {'error': 'No agreement associated'}

        discrepancies = []
        total_checks = 0
        failed_checks = 0

        for item in invoice.line_items or []:
            total_checks += 1
            
            rate = VerificationService._find_matching_rate(invoice.agreement, item)
            if not rate:
                failed_checks += 1
                continue

            expected_cost = rate.calculate_cost(
                quantity=item.get('quantity', 1),
                distance=item.get('distance', 0),
                weight=item.get('weight', 0)
            )
            actual_cost = item.get('amount', 0)
            
            if not is_within_tolerance(expected_cost, actual_cost, float(rate.tolerance_percentage)):
                InvoiceDiscrepancy.objects.create(
                    invoice=invoice,
                    rate_configuration=rate,
                    discrepancy_type='TOLERANCE_EXCEEDED',
                    description=f"Amount mismatch: {item.get('description', '')}",
                    expected_value=expected_cost,
                    actual_value=actual_cost,
                    difference=abs(actual_cost - expected_cost),
                    difference_percentage=round(abs(actual_cost - expected_cost) / expected_cost * 100, 2) if expected_cost > 0 else 0,
                    financial_impact=abs(actual_cost - expected_cost)
                )
                discrepancies.append(f"Line item {item.get('description', '')}: expected {expected_cost}, got {actual_cost}")
                failed_checks += 1

        invoice.status = 'DISCREPANCY' if failed_checks > 0 else 'VERIFIED'
        invoice.verified_at = timezone.now()
        invoice.save()

        return {
            'invoice_id': invoice_id,
            'status': invoice.status,
            'total_checks': total_checks,
            'failed_checks': failed_checks,
            'discrepancies': discrepancies
        }

    @staticmethod
    def _find_matching_rate(agreement, line_item: dict) -> RateConfiguration:
        """Find matching rate for a line item."""
        return agreement.rates.filter(
            is_active=True
        ).first()

    @staticmethod
    def process_excel_invoice(file_path: str) -> dict:
        """Process an invoice Excel file."""
        try:
            df = pd.read_excel(file_path)
            
            invoice_data = {
                'invoice_number': str(df.iloc[0]['Invoice Number']) if 'Invoice Number' in df.columns else '',
                'invoice_date': pd.to_datetime(df.iloc[0]['Invoice Date']).date() if 'Invoice Date' in df.columns else None,
                'total_amount': float(df.iloc[0]['Total Amount']) if 'Total Amount' in df.columns else 0,
                'line_items': []
            }
            
            for _, row in df.iterrows():
                if 'Line Number' in row:
                    invoice_data['line_items'].append({
                        'line_number': str(row.get('Line Number', '')),
                        'description': str(row.get('Description', '')),
                        'quantity': float(row.get('Quantity', 1)),
                        'amount': float(row.get('Amount', 0)),
                    })
            
            return invoice_data
        except Exception as e:
            return {'error': f'Failed to process Excel: {str(e)}'}
