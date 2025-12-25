from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('facility/<uuid:uuid>/', views.facility_detail, name='facility_detail'),
    path('api/counties/', views.api_counties, name='api_counties'),
]