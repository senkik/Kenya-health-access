from django.urls import path
from . import views

urlpatterns = [
    path('callback/', views.ussd_callback, name='ussd_callback'),
    path('sms-callback/', views.sms_callback, name='sms_callback'),
]