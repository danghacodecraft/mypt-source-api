from django.db import models

class Cron(models.Model):
    class Meta:
        db_table = 'mypt_setting_cron'
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    method = models.CharField(max_length=10, blank=False, null=False)
    url = models.TextField(blank=False, null=False)
    headers = models.JSONField(null=True)
    data = models.JSONField(null=True)
    params = models.JSONField(null=True)
    proxies = models.JSONField(null=True)
    schedule = models.TextField(blank=False, null=False)
    error_schedule = models.TextField(null=True, default=None)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(auto_now=True)