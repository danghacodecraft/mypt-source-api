from django.db import models

class CallAPILogger(models.Model):
    class Meta:
        db_table = 'mypt_setting_call_api_logger'
        
    id = models.AutoField(primary_key=True)
    url = models.TextField(blank=False, null=False)
    method = models.CharField(max_length=10, blank=False, null=False)
    data = models.JSONField(null=True, default=None)
    params = models.JSONField(null=True, default=None)
    headers = models.JSONField(null=True, default=None)
    result = models.TextField(null=True, default=None)
    called_at = models.DateTimeField(auto_now_add=True)
    