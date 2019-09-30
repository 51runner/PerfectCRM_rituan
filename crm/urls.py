from django.conf.urls import url, include
from crm import views

urlpatterns = [
    url(r'^$', views.index, name="sales_index"),
    url(r'^customer/(\d+)/enrollmet/$', views.enrollment, name="enrollment"),
    url(r'^customer/registration/(\d+)/(\w+)$', views.stu_registration, name="stu_registration"),
    url(r'^payment/(\d+)/$', views.payment, name="payment"),
    url(r'^payment_2/(\d+)/$', views.payment_2, name="payment_2"),
    url(r'^enrollment_rejection/(\d+)/$', views.enrollment_rejection, name="enrollment_rejection"),
    url(r'^customer/$', views.customer_list, name="customer_list"),

]
