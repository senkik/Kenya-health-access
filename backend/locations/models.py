from django.db import models

class County(models.Model):
    """47 Kenyan Counties"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)  # County codes: 001, 047, etc.
    capital = models.CharField(max_length=100)
    region = models.CharField(max_length=50, blank=True)  # Former province
    
    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Optional - Add these later when needed
# class Constituency(models.Model):
#     """Constituencies within counties"""
#     name = models.CharField(max_length=100)
#     county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='constituencies')
#     
#     class Meta:
#         verbose_name_plural = "Constituencies"
#         unique_together = ['name', 'county']
#     
#     def __str__(self):
#         return f"{self.name}, {self.county.name}"

# class Ward(models.Model):
#     """Wards within constituencies"""
#     name = models.CharField(max_length=100)
#     constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='wards')
#     
#     def __str__(self):
#         return f"{self.name}, {self.constituency.name}"