from django.db import models
import uuid
from locations.models import County

class FacilityType(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=20, default="🏥")
    
    class Meta:
        verbose_name_plural = "Facility Types"
    
    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('general', 'General Medicine'),
        ('specialist', 'Specialist Care'),
        ('emergency', 'Emergency Services'),
        ('diagnostic', 'Diagnostic Services'),
        ('maternal', 'Maternal & Child Health'),
        ('pharmacy', 'Pharmacy Services'),
    ])
    
    class Meta:
        verbose_name_plural = "Services"
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Facility(models.Model):
    name = models.CharField(max_length=200)
    facility_type = models.ForeignKey(FacilityType, on_delete=models.PROTECT)
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    constituency = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    services = models.ManyToManyField(Service, blank=True)
    emergency_available = models.BooleanField(default=False)
    ambulance_available = models.BooleanField(default=False)
    accepts_nhif = models.BooleanField(default=False)
    nhif_code = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateField(null=True, blank=True)
    opening_hours = models.TextField(blank=True)
    is_24_hours = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Real-time availability
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('emergency_only', 'Emergency Only'),
        ('closed', 'Closed'),
    ]
    availability_status = models.CharField(
        max_length=20, 
        choices=AVAILABILITY_CHOICES, 
        default='available'
    )
    last_status_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.county}"

    @property
    def average_rating(self):
        avg = self.reviews.filter(is_approved=True).aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def total_reviews(self):
        return self.reviews.filter(is_approved=True).count()

class Review(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    user_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True) # Defaulting to True for now, can be changed to False for moderation

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.facility.name} by {self.user_name}"