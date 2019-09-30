from django.shortcuts import render, HttpResponse, redirect
from king_admin import king_admin
import importlib
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from king_admin.utils import table_filter, table_sort, table_search, request_url
from king_admin.forms import create_model_form
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def index(request):
    print(king_admin.enabled_admin['crm']['customer'].model)
    return render(request, "king_admin/table_index.html", {'table_list': king_admin.enabled_admin})

@login_required
def display_table_objs(request, app_name, table_name):
    print("-->", app_name, table_name)

    # model_module = importlib.import_module('%s.models' % (app_name))
    # model_obj = getattr(model_module, table_name)
    admin_class = king_admin.enabled_admin[app_name][table_name]  # 获取数据的主入口

    if request.method == "POST":  # action来啦

        selected_ids = request.POST.get("selected_ids")
        action = request.POST.get("action")
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            return redirect(request.path)
        if hasattr(admin_class, action):
            action_func = getattr(admin_class, action)
            request._admin_action = action
            return action_func(admin_class, request, selected_objs)

    # object_list = admin_class.model.objects.all()
    object_list, filter_condtions = table_filter(request, admin_class)  # 过滤后的结果

    # request_url = '&' + str(filter_condtions).replace('\'', '').replace('{', '').replace('}', '').replace(':', '=') \
    #   .replace(',', '&').replace(' ', '')

    filter_url = request_url(request)

    object_list, search_key = table_search(request, admin_class, object_list)  # 搜索的结果

    object_list, orderby_key = table_sort(request, admin_class, object_list)  # 排序后的结果

    paginator = Paginator(object_list, admin_class.list_per_page)

    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_sets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_sets = paginator.page(paginator.num_pages)

    from king_admin.king_admin import CustomerAdmin

    return render(request, "admin/table_obj.html", {"admin_class": admin_class,
                                                    "query_sets": query_sets,
                                                    "filter_condtions": filter_condtions,
                                                    "object_list_count": object_list.count(),
                                                    "qq_search": admin_class.model._meta.object_name,
                                                    "orderby_key": orderby_key,
                                                    "previous_orderby": request.GET.get('o', ''),
                                                    "search_key": search_key,
                                                    "search_by": CustomerAdmin.search_fields,
                                                    "filter_url": filter_url})

@login_required
def table_obj_change(request, app_name, table_name, obj_id):
    """
    编辑or修改功能
    :param request:
    :param app_name:
    :param table_name:
    :param obj_id:
    :return:
    """
    admin_class = king_admin.enabled_admin[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == "POST":

        form_obj = model_form_class(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
    else:
        form_obj = model_form_class(instance=obj)
    return render(request, "admin/table_obj_change.html", {"form_obj": form_obj,
                                                           "admin_class": admin_class,
                                                           "app_name": app_name,
                                                           "table_name": table_name})

@login_required
def password_reset(request, app_name, table_name, obj_id):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    errors = {}
    if request.method == "POST":
        _password1 = request.POST.get("password1")
        _password2 = request.POST.get("password2")

        if _password1 == _password2:
            if len(_password1) > 5:
                obj.set_password(_password1)
                obj.save()
                return redirect(request.path.rstrip("password/"))
            else:
                errors["password_too_short"] = "密码长度不能少于6位！"

        else:
            errors["invalid_password"] = "两次密码不一致！"

    return render(request, "admin/password_reset.html", {"obj": obj, "errors": errors})

@login_required
def table_obj_add(request, app_name, table_name):
    """
    添加功能
    :param request:
    :param app_name:
    :param table_name:
    :return:
    """
    admin_class = king_admin.enabled_admin[app_name][table_name]
    admin_class.is_add_form = True
    model_form_class = create_model_form(request, admin_class)

    if request.method == "POST":
        form_obj = model_form_class(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(request.path.replace("/add/", "/"))
    else:
        form_obj = model_form_class()

    return render(request, "admin/table_obj_add.html", {"form_obj": form_obj,
                                                        "admin_class": admin_class})

@login_required
def table_obj_delete(request, app_name, table_name, obj_id):
    """
    删除功能
    :param request:
    :param app_name:
    :param table_name:
    :param obj_id:
    :return:
    """
    admin_class = king_admin.enabled_admin[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)
    errors = {}
    if admin_class.readnoly_table:
        errors = {"readnoly_table": "tables is readnoly ,obj [%s] cannot be deleted % obj "}
    else:
        errors = {}

    if request.method == "POST":
        if not admin_class.readnoly_table:
            obj.delete()
            return redirect("/king_admin/%s/%s/" % (app_name, table_name))

    return render(request, "admin/table_obj_delete.html", {"obj": obj,
                                                           "admin_class": admin_class,
                                                           "app_name": app_name,
                                                           "table_name": table_name,
                                                           "errors": errors
                                                           })
