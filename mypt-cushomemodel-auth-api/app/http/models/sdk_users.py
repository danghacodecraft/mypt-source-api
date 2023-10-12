from django.db import models

# Create your models here.
class SdkUsers(models.Model):
    class Meta:
        db_table = 'mypt_chm_auth_sdk_users'

    user_id = models.AutoField(primary_key=True)
    app_id = models.CharField(max_length=50)
    acc_username = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True)
    full_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    device_token = models.CharField(max_length=255)
    device_platform = models.CharField(max_length=30)
    device_info = models.CharField(max_length=1000)
    date_login = models.DateTimeField(null=True, default=None)
    date_latest_refresh_token = models.DateTimeField(null=True, default=None)
    app_version = models.CharField(max_length=50)
    is_deleted = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(null=True, default=None)
