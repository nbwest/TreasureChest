from __future__ import unicode_literals

import calendar
import datetime

from django.utils.html import avoid_wrapping
from django.utils.timezone import is_aware, utc
from django.utils.translation import ugettext, ungettext_lazy

from django import template
from django.template import Variable, VariableDoesNotExist
register = template.Library()

@register.filter('klass')

def klass(ob):
    return ob.__class__.__name__






TIMESINCE_CHUNKS = (
    (365, ungettext_lazy('%d year', '%d years')),
    (30, ungettext_lazy('%d month', '%d months')),
    (7, ungettext_lazy('%d week', '%d weeks')),
    (1, ungettext_lazy('%d day', '%d days')),
)


@register.filter("timebetween", is_safe=False)
def timebetween_filter(value, arg=None):
    """Formats a date as the time until that date (i.e. "4 days, 6 hours")."""
    if not value:
        return ''
    try:
        return timebetween(value, arg)
    except (ValueError, TypeError):
        return ''


def timebetween(d, now=None):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 dyas".  If d occurs after now,
    then "now" is returned.

    Units used are years, months, weeks and days.
    Time is ignored.

    Adapted from
    http://web.archive.org/web/20060617175230/http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)

    delta = (d - now)

    # Deal with leapyears by subtracing the number of leapdays
    delta -= datetime.timedelta(calendar.leapdays(d.year, now.year))

    # ignore time
    since = delta.days

    #add negative for time in the past
    prefix=""
    if since < 0:
        since=-since
        prefix="-"

    if since == 0:
        return avoid_wrapping(ugettext('today'))

    for i, (days, name) in enumerate(TIMESINCE_CHUNKS):
        count = since // days
        if count != 0:
            break

    result = avoid_wrapping(prefix + name % count)


    return result


#allows concatination for form fields names plus exta argument, returns rendered output
@register.simple_tag
def form_field_concat(form, prefix, suffix, *args, **kwargs):

    if prefix+suffix not in form.fields:
        return None

    field= form.fields[prefix+suffix]
    return field.widget.render(prefix+suffix,field.initial,attrs=kwargs)
