from django.shortcuts import render, HttpResponse, redirect
from crm import forms, models
import string, random
from django.db import IntegrityError
from django.core.cache import cache


# Create your views here.


def index(request):
    return render(request, "index.html")


def customer_list(request):
    return render(request, "sales/customers.html")


def stu_registration(request, enroll_id, random_str):
    # if cache.get(enroll_id) == random_str:

    enroll_obj = models.Enrollment.objects.get(id=enroll_id)

    if request.method == "POST":
        customer_form = forms.CustomerForm(request.POST, instance=enroll_obj.customer)
        if customer_form.is_valid():
            customer_form.save()
            enroll_obj.contract_agreed = True
            enroll_obj.save()
            return render(request, "sales/stu_registration.html", {"customer_form": customer_form,
                                                                   "enroll_obj": enroll_obj,
                                                                   "status": 1})

    else:
        if enroll_obj.contract_agreed == True:
            status = 1
        else:
            status = 0

        customer_form = forms.CustomerForm(instance=enroll_obj.customer)
    print("enroll_obj_id",enroll_obj.id)
    return render(request, "sales/stu_registration.html", {"customer_form": customer_form,
                                                           "enroll_obj": enroll_obj,
                                                           "status": status})
    # else:
    #     return HttpResponse("链接已经失效！")


def enrollment(request, customer_id):
    customer_obj = models.Customer.objects.get(id=customer_id)
    msgs = {}
    if request.method == "POST":
        enroll_form = forms.EnrollmentForm(request.POST)
        if enroll_form.is_valid():
            msg = """请将此链接发送给客户进行填写
            http://127.0.0.1:8080/crm/customer/registration/{enroll_obj_id}/{random_str}"""
            try:
                print("cleandata", enroll_form.cleaned_data)
                enroll_form.cleaned_data['customer'] = customer_obj
                enroll_obj = models.Enrollment.objects.create(**enroll_form.cleaned_data)

                random_str = "".join(random.sample(string.ascii_lowercase + string.digits, 8))

                msgs['msg'] = msg.format(enroll_obj_id=enroll_obj.id, random_str=random_str)
                print("enroll_obj1", enroll_obj.id)

            except IntegrityError as e:
                enroll_obj = models.Enrollment.objects.get(customer_id=customer_obj.id,
                                                           enrolled_class_id=enroll_form.cleaned_data[
                                                               "enrolled_class"].id)

                if enroll_obj.contract_agreed:  # 证明学生已经同意了！
                    return redirect("/crm/payment/%s/" % enroll_obj.id)

                enroll_form.add_error("__all__", "该用户的此条报名信息已存在,不能重复创建！")
                random_str = "".join(random.sample(string.ascii_lowercase + string.digits, 8))

                cache.set(enroll_obj.id, random_str, 3000)
                msgs['msg'] = msg.format(enroll_obj_id=enroll_obj.id, random_str=random_str)

    else:
        enroll_form = forms.EnrollmentForm()

    return render(request, "sales/enrollment.html",
                  {"enroll_form": enroll_form, "customer_obj": customer_obj, "msgs": msgs})


def payment(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_form = forms.EnrollmentForm(instance=enroll_obj)
    print(enroll_form)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)

    return render(request, "sales/payment.html",
                  {"enroll_obj": enroll_obj, "customer_form": customer_form, "enroll_form": enroll_form})


def enrollment_rejection(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()

    return redirect("/crm/customer/%s/enrollmet/" % enroll_obj.customer.id)


def payment_2(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)

    errors = []
    if request.method == "POST":
        payment_amount = request.POST.get("amount")

        print("payment_amount:", payment_amount)

        if payment_amount:
            payment_form = int(payment_amount)

            if payment_form < 500:
                errors.append("缴费金额不得低于500元")
            else:
                payment_obj = models.Payment.objects.create(
                    customer=enroll_obj.customer,
                    course=enroll_obj.enrolled_class.course,
                    amount=payment_amount,
                    consultant=enroll_obj.consultant
                )
                enroll_obj.contract_agreed = True
                enroll_obj.save()

                enroll_obj.customer.status = 0
                enroll_obj.customer.save()

                return redirect("/king_admin/crm/customer/")
    print(errors)

    return render(request, "sales/payment_2.html", {"enroll_obj": enroll_obj, "errors": errors})
