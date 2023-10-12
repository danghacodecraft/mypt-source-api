import datetime
from django.db import models

class QueueTask(models.Model):
    class Meta:
        db_table = "mypt_queue_tasks"
        
    id = models.CharField(max_length=1000, primary_key=True)
    task = models.CharField(max_length=2000, blank=False, null=False)
    eta = models.DateTimeField(null=True, default=None)
    expires = models.DateTimeField(null=True, default=None)
    retries = models.IntegerField(null=False, default=0)
    kwargs = models.JSONField(null=True, default=None)
    status = models.CharField(max_length=100, null=False, blank=False, default="IN_QUEUE")
    result = models.TextField(blank=True, null=True, default=None)
    started_at = models.DateTimeField(null=True, default=None)
    done_at = models.DateTimeField(null=True, default=None)
    revoked_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)
    
    def soft_delete(self):
        self.deleted_at = datetime.datetime.now()
        self.save(update_fields=["deleted_at"])
