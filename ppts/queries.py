from django.db.models import F
from django.db.models import fields
from django.db.models import ExpressionWrapper

from ppts.models import Record
from ppts.models import RecordType


STILL_OPEN = [
    'Accepted',
    'Actions Pending',
    'Application Accepted',
    # 'Approved',
    # 'Closed',
    # 'Closed - Approved',
    # 'Closed - Complete',
    # 'Closed - Withdrawn',
    # 'Complete',
    # 'Denied',
    # 'Disapproved',
    'Incomplete',
    'On Hold',
    'Open',
    'Pending',
    'Pending Review',
    'Submitted',
    'Under Review',
    # 'Withdrawn',
]

COMPLETE = [
    # 'Accepted',
    # 'Actions Pending',
    # 'Application Accepted',
    'Approved',
    'Closed',
    'Closed - Approved',
    'Closed - Complete',
    'Closed - Withdrawn',
    'Complete',
    'Denied',
    'Disapproved',
    # 'Incomplete',
    # 'On Hold',
    # 'Open',
    # 'Pending',
    # 'Pending Review',
    # 'Submitted',
    # 'Under Review',
    'Withdrawn',
]


def age_by_record_type(category="PRJ"):
    """age_by_record_type annotates Records of given record type with age.

    It returns a Record queryset containing only Records of the given record
    type category, annotated with the age of that record, if it has both a
    date_opened and a date_closed."""
    prj = RecordType.objects.get(category=category)
    duration = ExpressionWrapper(
        F('date_closed') - F('date_opened'),
        output_field=fields.DurationField())

    r = (Record.objects
         .filter(record_type=prj)
         .exclude(date_opened__isnull=True)
         .exclude(date_closed__isnull=True)
         .annotate(age=duration))
    return r
