from django.db import models

# Create your models here.
class SdkUserPermission(models.Model):
    class Meta:
        db_table = 'mypt_chm_auth_sdk_user_permission'

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_code = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, default=None)
    created_by = models.IntegerField(null=True, default=None)
