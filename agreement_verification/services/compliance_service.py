"""Compliance service for rule engine execution."""
from apps.compliance.models.rules import ComplianceRule, ComplianceCheck, ComplianceReport

class ComplianceService:
    """Service for compliance checking."""

    @staticmethod
    def execute_rule(rule: ComplianceRule, entity) -> dict:
        """Execute a single compliance rule."""
        result = {'status': 'PENDING', 'message': '', 'details': {}}
        
        try:
            config = rule.rule_config
            field = config.get('field')
            operator = config.get('operator')
            expected_value = config.get('value')
            
            actual_value = ComplianceService._get_field_value(entity, field)
            
            passed = False
            if operator == 'equals':
                passed = actual_value == expected_value
            elif operator == 'greater_than':
                passed = actual_value > expected_value
            elif operator == 'less_than':
                passed = actual_value < expected_value
            elif operator == 'not_empty':
                passed = bool(actual_value)
            
            result['status'] = 'PASSED' if passed else 'FAILED'
            result['message'] = rule.error_message if not passed else 'Check passed'
            result['details'] = {'expected': expected_value, 'actual': actual_value}
            
        except Exception as e:
            result['status'] = 'WARNING'
            result['message'] = f'Error: {str(e)}'
        
        return result

    @staticmethod
    def _get_field_value(entity, field_path: str):
        """Get field value from entity."""
        value = entity
        for part in field_path.split('.'):
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
        return value
