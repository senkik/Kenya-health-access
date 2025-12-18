from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('facility/<uuid:uuid>/', views.facility_detail, name='facility_detail'),
]