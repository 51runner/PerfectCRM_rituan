# -*- coding: UTF-8 -*-
# _Author:Rea
from django.shortcuts import render, redirect
from crm import models

enabled_admin = {}


class BaseAdmin(object):
    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 20
    readonly_fields = []
    actions = ["delete_selected_objs"]
    readonly_table = False
    modelform_exclude_fields = []

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        # print("---> delete_selected_objs",request, queryset)
        if self.readonly_table:
            errors = {"readnoly_table": "This table is readonly ,cannot be deleted obj"}
        else:
            errors = {}

        if request.POST.get("delete_confirm") == "yes":
            if not self.readonly_table:
                querysets.delete()
            return redirect('/king_admin/%s/%s/' % (app_name, table_name))
        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request, 'king_admin/table_objs_delete.html', {"objs": querysets,
                                                                     "admin_class": self,
                                                                     "app_name": app_name,
                                                                     "table_name": table_name,
                                                                     "selected_ids": selected_ids,
                                                                     "action": request._admin_action,
                                                                     "errors": errors})

    def default_form_validation(self):
        """用户可在此进行自定义表单验证，相当于django form的clean方法"""
        pass


class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq', 'name', 'source', 'consultant', 'consult_course', 'date', 'enroll', 'status']
    list_filter = ['source', 'consultant', 'consult_course', 'status', 'date']
    search_fields = ("qq", "name", "consultant__name")
    raw_id_fields = ("consult_course",)
    filter_horizontal = ("tags",)
    list_editable = ("status",)
    list_per_page = 5
    readonly_fields = ["qq", "consultant", "tags"]
    readonly_table = True

    # modelform_exclude_fields = []

    def enroll(self):

        if self.instance.status == 0:
            line_name = "报名新课程"
        else:
            line_name = "报名课程"

        return """ <a href="/crm/customer/%s/enrollmet/"  target="_blank">%s</a> """ % (self.instance.id, line_name)

    enroll.display_name = "报名链接"

    def default_form_validation(self):
        # print("-------customer validation", self)
        print("----instance:", self.instance)
        consult_content = self.cleaned_data.get("content", "")
        if len(consult_content) < 15:
            return self.ValidationError(
                ("Field %(field)s 咨询内容不能少于15个字符"),
                code='invalid',
                params={'field': "content", }
            )

    # 单个表单做认证
    def clean_name(self):
        if not self.cleaned_data["name"]:
            self.add_error('name', "不能为空")


class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('id', 'customer', 'consultant', 'date')


class UserProfileAdmin(BaseAdmin):
    list_display = ('email', 'name')
    readonly_fields = ('password',)
    modelform_exclude_fields = ["last_login", ]
    filter_horizontal = ("user_permissions", "groups")


def register(models_class, admin_class=None):
    # models.UserProfile._meta.app_label 'crm'            项目app名字
    # models.UserProfile._meta.model_name 'userprofile'   表名

    # 判断有没有在字典当中 没有则加入
    if models_class._meta.app_label not in enabled_admin:
        enabled_admin[models_class._meta.app_label] = {}  # enabled_admin['crm'] = {}

    # admin_obj = admin_class()
    admin_class.model = models_class  # 绑定model 对象和admin 类

    enabled_admin[models_class._meta.app_label][models_class._meta.model_name] = admin_class


register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)

# print(enabled_admin)
# {'crm': {'customer': <class 'king_admin.king_admin.CustomerAdmin'>, 'customerfollowup': <class 'king_admin.king_admin.CustomerFollowUpAdmin'>}}
