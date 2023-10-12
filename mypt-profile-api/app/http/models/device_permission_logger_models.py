from django.db import models


class DevicePermissionLogger(models.Model):
    class Meta:
        db_table = 'mypt_profile_device_permission_logger'

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    permission = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    log_at = models.DateTimeField(auto_now_add=True)


class DevicePermissionLastChange(models.Model):
    class Meta:
        db_table = 'mypt_profile_device_permission_last_change'

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    permission = models.CharField(max_length=50)
    status_after_change = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DevicePermissions(models.Model):
    class Meta:
        db_table = 'mypt_profile_device_permissions_information'

    # id  = models.AutoField(primary_key=True)
    permission_code = models.CharField(max_length=50, primary_key=True)
    permission_name = models.CharField(max_length=200, default="")
    permission_desc = models.TextField(default="")
    is_active = models.BooleanField(default=True)
