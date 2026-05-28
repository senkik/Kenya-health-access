from django.db import models

class MFLSyncLog(models.Model):
    """Track MFL sync operations"""
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='running')
    facilities_created = models.IntegerField(default=0)
    facilities_updated = models.IntegerField(default=0)
    facilities_skipped = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Sync {self.id} - {self.started_at} - {self.status}"
