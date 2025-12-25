from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Facility
from locations.models import County

def home(request):
    """Home page"""
    return render(request, 'home.html')

def search(request):
    """Search page"""
    return render(request, 'search.html')

def facility_detail(request, uuid):
    """Facility detail page"""
   
    return render(request, 'facility_detail.html')

def api_counties(request):
    """API endpoint for counties (JSON)"""
    counties = County.objects.all().values('id', 'name', 'code', 'capital')
    return JsonResponse(list(counties), safe=False)