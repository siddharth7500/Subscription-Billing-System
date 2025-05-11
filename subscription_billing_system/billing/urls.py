from django.urls import path
from .views import *
urlpatterns = [
    path('api/select_plan/', select_plan, name='my_plan'),
    path('api/my_plan/', MyPlanAPIView.as_view(), name='my_plan'),
    path('api/my_invoices/', MyInvoicesAPIView.as_view(), name='my_invoices'),
    path('api/payment_status/', PaymentStatusAPIView.as_view(), name='payment_status'),
]