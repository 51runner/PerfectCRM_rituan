# -*- coding: UTF-8 -*-
# _Author:Rea

from django.utils.translation import ugettext as _
from django.forms import forms, ModelForm
from django.forms import ValidationError
from crm import models


class CustomerModelForm(ModelForm):
    class Meta:
        model = models.Customer
        fields = "__all__"


def create_model_form(request, admin_class):
    """动态生成MODEL FORM"""

    def __new__(cls, *args, **kwargs):
        # super(CustomerForm,self).__new__(*args,**kwargs)
        # self.fields['customer_note'].widget.attrs['class'] = 'form-control'

        for field_name, filter_obj in cls.base_fields.items():
            filter_obj.widget.attrs['class'] = 'form-control'

            # add user second prohibit chenge [qq and constant]

            if not hasattr(admin_class, "is_add_form"): # 代表这是添加form，不需要disabled
                if field_name in admin_class.readonly_fields:
                    filter_obj.widget.attrs["disabled"] = "disabled"

            if hasattr(admin_class, "clean_%s" % field_name):
                field_clean_func = getattr(admin_class, "clean_%s" % field_name)
                setattr(cls, "clean_%s" % field_name, field_clean_func)

        return ModelForm.__new__(cls)

    def default_clean(self):
        """给所有的form默认加一个clean验证"""
        # print("-----running instance", self.instance)  # instance 是实例的意思

        error_list = []

        if self.instance.id:  # 这是修改的表单
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance, field)  # val in db  //field 是在king_admin中的readonly_fields
                if hasattr(field_val, "select_related"):  # m2m
                    m2m_objs = getattr(field_val, "select_related")().select_related()
                    m2m_vals = [i[0] for i in m2m_objs.values_list("id")]
                    set_m2m_vals = set(m2m_vals)
                    set_m2m_vals_from_fromtend = set([i.id for i in self.cleaned_data.get(field)])
                    if set_m2m_vals != set_m2m_vals_from_fromtend:
                        self.add_error(field, "readonly field")
                    continue

                field_val_from_frontend = self.cleaned_data.get(field)  # val in frontend 前端form表单提交的数据
                if field_val != field_val_from_frontend:
                    error_list.append(ValidationError(
                        _("Field %(field)s is readonly,date should be %(val)s"),
                        code='invalid',
                        params={'field': field, 'val': field_val}
                    ))

        # readnoly_table check
        if admin_class.readonly_table:
            raise ValidationError(
                        _("table is readonly,cannot be modified or added"),
                        code='invalid',
                    )

        # invoke user's cotomized form validation
        self.ValidationError = ValidationError
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)

        if error_list:
            raise ValidationError(error_list)

    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields

    attrs = {"Meta": Meta}

    _model_form_class = type("DynamicModelForm", (ModelForm,), attrs)
    setattr(_model_form_class, '__new__', __new__)
    setattr(_model_form_class, 'clean', default_clean)
    return _model_form_class
