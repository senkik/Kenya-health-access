from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    capital = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']
    
    def __str__(self):
        return self.name