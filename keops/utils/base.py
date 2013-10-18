import datetime
import decimal
from django.utils import formats
from django.db import models

def field_text(value, obj=None, field=None, disp_field=None):
    if value is None:
        return ''
    elif isinstance(value, models.Model):
        return {'id': value.pk, 'text': str(value)}
    elif field != disp_field:
        return {'id': value, 'text': getattr(obj, disp_field)()}
    elif callable(value):
        return value()
    elif isinstance(value, (float, decimal.Decimal)):
        return str(value)
    elif isinstance(value, (int, str)):
        return value
    elif isinstance(value, datetime.date):
        return formats.date_format(value, 'SHORT_DATE_FORMAT')
    elif isinstance(value, datetime.datetime):
        return formats.date_format(value, 'SHORT_DATETIME_FORMAT')
    else:
        return str(value)

