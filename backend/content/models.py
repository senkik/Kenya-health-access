from django.db import models
from django.utils.text import slugify

class HealthArticle(models.Model):
    CATEGORIES = [
        ('general', 'General Health'),
        ('maternal', 'Maternal Health'),
        ('child', 'Child Health'),
        ('nutrition', 'Nutrition'),
        ('disease', 'Disease Prevention'),
        ('mental', 'Mental Health'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    author = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en', choices=[('en', 'English'), ('sw', 'Swahili')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300] + '...'
        super().save(*args, **kwargs)

class HealthTip(models.Model):
    tip = models.CharField(max_length=160)
    category = models.CharField(max_length=50)
    language = models.CharField(max_length=10, default='sw', choices=[('en', 'English'), ('sw', 'Swahili')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tip[:50]}..."