#!/usr/bin/env python
# coding: utf-8

from django import template
from django.utils.safestring import mark_safe

register = template.Library()



#---------------------------------------------------------------------------------------------------
@register.filter
def jsonify(o):
    return mark_safe(json.dumps(o))
