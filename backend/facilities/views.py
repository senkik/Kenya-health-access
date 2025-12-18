from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Facility

def home(request):
    return HttpResponse("""
        <h1>🇰🇪 Kenya Health Access</h1>
        <p>Welcome to Kenya Health Access Platform</p>
        <ul>
            <li><a href="/admin/">Admin Panel</a></li>
            <li><a href="/api/">API Browser</a></li>
            <li><a href="/api/facilities/">Facilities List</a></li>
        </ul>
        <p>USSD: Dial *384#</p>
    """)

def facility_detail(request, uuid):
    facility = get_object_or_404(Facility, uuid=uuid)
    return HttpResponse(f"""
        <h1>{facility.name}</h1>
        <p><strong>County:</strong> {facility.county}</p>
        <p><strong>Type:</strong> {facility.facility_type.name}</p>
        <p><strong>Status:</strong> {'Open 24/7' if facility.is_24_hours else 'Check hours'}</p>
        <br>
        <a href="/">Back to Home</a>
    """)