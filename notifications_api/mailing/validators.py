from django.core.validators import RegexValidator

validate_operator_code = RegexValidator(regex=r'^\d{3}$', message='Operator code must be 3 digits')
validate_phone_number = RegexValidator(regex=r'^7\d{10}$', message='Phone number in format 7XXXXXXXXXX (X - digit 1-9)')
