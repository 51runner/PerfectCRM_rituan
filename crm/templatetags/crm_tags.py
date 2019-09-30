# -*- coding: UTF-8 -*-
# _Author:Rea

from django import template
from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta

register = template.Library()


@register.simple_tag
def render_enroll_contaract(enroll_obj):
    return enroll_obj.enrolled_class.contract.template.\
        format(stu_name=enroll_obj.customer.name)
