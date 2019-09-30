# -*- coding: UTF-8 -*-
# _Author:Rea
from django.db.models import Q


def table_filter(request, admin_class):
    '''进行条件过滤并返回过滤后的数据'''

    filter_conditions = {}
    key = ['page', 'o', '_q']

    for k, v in request.GET.items():
        # if k == 'page' or k == 'o':  # 保留的关键字
        if k in key:
            continue
        if v.strip():
            filter_conditions[k] = v.strip()

    return admin_class.model.objects.filter(**filter_conditions).order_by("-id"), filter_conditions


def table_sort(request, admin_class, objs):
    orderby_key = request.GET.get("o")
    if orderby_key:
        res = objs.order_by(orderby_key)

        if orderby_key.startswith("-"):
            orderby_key = orderby_key.strip("-")
        else:
            orderby_key = "-%s" % orderby_key
    else:
        res = objs

    return res, orderby_key


def table_search(request, admin_class, object_list):
    search_key = request.GET.get("_q", "")
    q_obj = Q()
    q_obj.connector = "OR"
    for column in admin_class.search_fields:
        q_obj.children.append(("{}__contains".format(column), search_key))

    res = object_list.filter(q_obj)
    return res, search_key


# 过滤URL
def request_url(request):
    filter_link = {}
    for k, v in request.GET.items():
        if v.strip() and k not in filter_link:
            filter_link[k] = v

    request_url = str(filter_link).replace('\'', '').replace('{', '').replace('}', '').replace(':', '=') \
                      .replace(',', '&').replace(' ', '') + '&'
    return request_url.strip()
