# -*- coding: UTF-8 -*-
# _Author:Rea

from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta

register = template.Library()


@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name_plural


@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all


@register.simple_tag
def build_table_row(request, obj, admin_class):
    row_ele = ""

    btn = ""
    for column in admin_class.list_display:
        field_obj = obj._meta.get_field(column)

        if field_obj.choices:  # choices type
            column_data = getattr(obj, "get_%s_display" % column)()
            if column == 'status':
                btn = "btn btn-info btn-rounded btn-sm" if column_data == '已报名' else 'btn btn-warning btn-rounded btn-sm'

        else:
            # 通过反射取出
            column_data = getattr(obj, column)

        if type(column_data).__name__ == 'datetime':
            column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")

        if type(column_data).__name__ == 'int':
            # 为a标签加上chenge链接
            column_data = "<a href='{request_path}{obj_id}/change/'>{data}</a>".format(request_path=request.path,
                                                                                       obj_id=obj.id, data=column_data)

        row_ele += "<td class='%s'>%s</td>" % (btn, column_data)

    return mark_safe(row_ele)


@register.simple_tag
def build_paginators(query_sets, filter_condtions, previous_orderby, search_key):
    """返回整个分页元素"""
    page_btns = ''
    filters = ""
    for k, v in filter_condtions.items():
        filters += "&%s=%s" % (k, v)

    added_dot_ele = False
    for page_num in query_sets.paginator.page_range:
        if page_num < 3 or page_num > query_sets.paginator.num_pages - 2 or \
                        abs(query_sets.number - page_num) <= 2:  # 代表最前两页或者最后两页
            ele_class = ""
            if query_sets.number == page_num:
                added_dot_ele = False
                ele_class = "active"
            page_btns += '''<li class={}><a href="?page={}{}&o={}&_q={}">{}</a></li>'''.format(ele_class, page_num,
                                                                                               filters,
                                                                                               previous_orderby,
                                                                                               search_key, page_num)
        else:  # 显示...
            if added_dot_ele == False:
                page_btns += '<li><a>..</a></li>'
                added_dot_ele = True
    return mark_safe(page_btns)


# 分页
@register.simple_tag
def render_page_ele(loop_counter, query_sets, filter_condtions):
    filters = ""
    for k, v in filter_condtions.items():
        filters += "&%s=%s" % (k, v)

    if loop_counter < 3 or loop_counter > query_sets.paginator.num_pages - 2:  # 代表前两页 or 最后两页
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class={}><a href="?page={}{}">{}</a></li>'''.format(ele_class, loop_counter, filters, loop_counter)
        return mark_safe(ele)

    if abs(query_sets.number - loop_counter) <= 2:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class={}><a href="?page={}{}">{}</a></li>'''.format(ele_class, loop_counter, filters, loop_counter)
        return mark_safe(ele)
    else:
        return '...'


# 过滤
@register.simple_tag
def render_filter_ele(filter_field, admin_class, filter_condtions):
    # select_ele = """<select class="form-control" name='{}' ><option value=''>未选</option>""".format(filter_field)
    select_ele = """<select class="form-control" name='{filter_field}' ><option value=''>未选</option>"""
    field_obj = admin_class.model._meta.get_field(filter_field)  # 获取字段对象
    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            if filter_condtions.get(filter_field) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value="{}" {}>{}</option>'''.format(choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ == 'ForeignKey':
        selected = ''
        for choice_item in field_obj.get_choices()[1:]:
            if filter_condtions.get(filter_field) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value="{}" {}>{}</option>'''.format(choice_item[0], selected, choice_item[1])
            selected = ''
    if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
        date_els = []
        date_els.append(['今天', datetime.now().date()])
        date_els.append(['昨天', datetime.now().date() - timedelta(days=1)])
        date_els.append(['近7天', datetime.now().date() - timedelta(days=7)])
        date_els.append(['本月', datetime.now().date().replace(day=1)])
        date_els.append(['近30天', datetime.now().date() - timedelta(days=30)])
        date_els.append(['近3个月', datetime.now().date() - timedelta(days=90)])
        date_els.append(['近半年', datetime.now().date() - timedelta(days=180)])
        date_els.append(['本年', datetime.now().date().replace(month=1, day=1)])  # 例如20170101
        date_els.append(['近一年', datetime.now().date() - timedelta(days=365)])
        selected = ''

        for item in date_els:
            select_ele += '''<option value="{}" {}>{}</option>'''.format(item[1], selected, item[0])

        filter_field_name = "%s__gte" % filter_field




    else:
        filter_field_name = filter_field
    select_ele += "</select>"
    select_ele = select_ele.format(filter_field=filter_field_name)
    return mark_safe(select_ele)


@register.simple_tag
def build_table_header_column(column, orderby_key, filter_condtions):
    filters = ''
    for k, v in filter_condtions.items():
        filters += "&{}={}".format(k, v)

    ele = '''<th><a href="?{filters}&o={orderby_key}">{column}</a>
    {sort_icon}</th>'''
    if orderby_key:

        if orderby_key.startswith('-'):
            sort_icon = '''<span class="glyphicon glyphicon-chevron-up"></span>'''
        else:
            sort_icon = '''<span class="glyphicon glyphicon-chevron-down"></span>'''

        if orderby_key.strip("-") == column:  # 排序的就是這个字段
            orderby_key = orderby_key

        else:
            orderby_key = column
            sort_icon = ''

    else:
        orderby_key = column
        sort_icon = ''

    return mark_safe(ele.format(filters=filters, orderby_key=orderby_key, column=column, sort_icon=sort_icon))


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_m2m_obj_list(admin_class, field, form_obj):
    """
    返回m2m所有待选数据
    :param admin_class:
    :param field:
    :return:
    """
    # 表结构对象的某个字段
    field_obj = getattr(admin_class.model, field.name)
    all_obj_list = field_obj.rel.to.objects.all()

    # 单条数据的对象中的某个字段 / 已选中的数据
    if form_obj.instance.id:  # 返回布尔值是否为空
        # 已选中的数据
        obj_instance_field = getattr(form_obj.instance, field.name)
        selected_obj_list = obj_instance_field.all()
    else:  # 代表這是在创建新的一条记录
        return all_obj_list

    standby_obj_list = []
    for obj in all_obj_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)

    return standby_obj_list


@register.simple_tag
def get_m2m_selected_obj_list(form_obj, field):
    """返回已选择的m2m数据"""
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field.name)
        return field_obj.all()



def recursive_related_objs_lookup(objs):
    #model_name = objs[0]._meta.model_name
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = '''<li> %s: %s </li>'''%(obj._meta.verbose_name,obj.__str__().strip("<>"))
        ul_ele += li_ele

        #for local many to many
        #print("------- obj._meta.local_many_to_many", obj._meta.local_many_to_many)
        for m2m_field in obj._meta.local_many_to_many: #把所有跟这个对象直接关联的m2m字段取出来了
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name) #getattr(customer, 'tags')
            for o in m2m_field_obj.select_related():# customer.tags.select_related()
                li_ele = '''<li> %s: %s </li>''' % (m2m_field.verbose_name, o.__str__().strip("<>"))
                sub_ul_ele +=li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele  #最终跟最外层的ul相拼接


        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():

                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    print("-------ManyToManyRel",accessor_obj,related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                        target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele ="<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li> %s: %s </li>''' % (o._meta.verbose_name, o.__str__().strip("<>"))
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj,related_obj.get_accessor_name()): # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj,related_obj.get_accessor_name())
                #上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj,'select_related'): # slect_related() == all()
                    target_objs = accessor_obj.select_related() #.filter(**filter_coditions)
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    print("one to one i guess:",accessor_obj)
                    target_objs = accessor_obj

                if len(target_objs) >0:
                    #print("\033[31;1mdeeper layer lookup -------\033[0m")
                    #nodes = recursive_related_objs_lookup(target_objs,model_name)
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele +="</ul>"
    return ul_ele


@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    #objs = [objs,] #fake
    if objs:
        model_class = objs[0]._meta.model
        mode_name = objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))