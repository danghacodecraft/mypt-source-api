from django.db import models

# Create your models here.
class UserPermission(models.Model):
    class Meta:
        db_table = 'mypt_auth_user_permission'

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_code = models.CharField(max_length=100)
    child_depart = models.CharField(max_length=5000, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, default=None)
    created_by = models.IntegerField(null=True, default=None)
