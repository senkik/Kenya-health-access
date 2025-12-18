from django.db import models
import json

class USSDsession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    menu_level = models.CharField(max_length=50, default='main')
    session_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "USSD Sessions"
    
    def __str__(self):
        return f"{self.phone_number} - {self.menu_level}"
    