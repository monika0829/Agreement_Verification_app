"""Helper functions."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

def is_within_tolerance(expected: float, actual: float, tolerance_pct: float) -> bool:
    """Check if actual value is within tolerance percentage of expected."""
    if expected == 0:
        return actual == 0
    difference = abs(expected - actual)
    tolerance_amount = (expected * tolerance_pct) / 100
    return difference <= tolerance_amount

def generate_reference_number(prefix: str) -> str:
    """Generate unique reference number."""
    import uuid
    timestamp = datetime.now().strftime('%Y%m%d')
    unique = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{timestamp}-{unique}"

def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)

def get_date_range_for_period(period: str) -> tuple:
    """Get date range for a period."""
    today = datetime.now().date()
    if period == 'today':
        return today, today
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    elif period == 'month':
        start = today.replace(day=1)
        next_month = (start + timedelta(days=32)).replace(day=1)
        return start, next_month - timedelta(days=1)
    return today, today
