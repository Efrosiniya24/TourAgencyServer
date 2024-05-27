from datetime import datetime
from rest_framework.exceptions import ValidationError

def parse_custom_date(value):
    for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValidationError('Date has wrong format. Use one of these formats instead: YYYY-MM-DD or DD.MM.YYYY.')
