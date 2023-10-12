from django.db import models


# Create your models here.
class ApiCallLog(models.Model):
    class Meta:
        db_table = 'mypt_chm_api_call_log'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    api_url = models.CharField(max_length=255, null=True, blank=False)
    api_env = models.CharField(max_length=255, null=True, blank=False)
    api_input = models.CharField(max_length=255, null=True, blank=False)
    api_output = models.CharField(max_length=255, null=True, blank=False)
    device_id = models.CharField(max_length=255, null=True, blank=False)
    device_name = models.CharField(max_length=255, null=True, blank=False)
    device_token = models.CharField(max_length=255, null=True, blank=False)
    device_platform = models.CharField(max_length=50, null=True, blank=False)
    sdk_user_id = models.BigIntegerField(null=False, blank=False)
    app_id = models.CharField(max_length=50, null=False, blank=False)
    sdk_acc_username = models.CharField(max_length=255, null=True, blank=False)
    date_called = models.DateTimeField(auto_created=True)

    def __str__(self):
        return self.api_url
