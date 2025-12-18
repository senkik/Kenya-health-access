from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'counties', views.CountyViewSet, basename='county')
router.register(r'facility-types', views.FacilityTypeViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'facilities', views.FacilityViewSet)
router.register(r'articles', views.HealthArticleViewSet, basename='article')
router.register(r'health-tips', views.HealthTipViewSet, basename='health-tip')  # Add this line

urlpatterns = [
    path('', include(router.urls)),
    path('facilities/search/', views.FacilityViewSet.as_view({'get': 'search'}), name='facility-search'),
    path('facilities/by-county/', views.FacilityViewSet.as_view({'get': 'by_county'}), name='facilities-by-county'),
    path('health-tips/random/', views.HealthTipViewSet.as_view({'get': 'random'}), name='random-health-tip'),
]