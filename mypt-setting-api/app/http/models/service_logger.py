from django.db import models

class ServiceLogger(models.Model):
    class Meta:
        db_table = 'mypt_setting_service_logger'
        
    id = models.AutoField(primary_key=True)
    path = models.TextField(blank=False, null=False)
    user_id = models.IntegerField(null=True, default=None)
    data = models.JSONField()
    params = models.JSONField()
    headers = models.JSONField()
    result = models.TextField(null=False, blank=True)
    called_at = models.DateTimeField(auto_now_add=True)
    