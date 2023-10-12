from django.db import models


# Create your models here.
class CurrentContractInfoLog(models.Model):

    class Meta:
        db_table = 'mypt_chm_current_contract_info_log'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    contract_code = models.CharField(max_length=255, null=False, blank=False)
    regions = models.CharField(max_length=255, null=False, blank=False)
    branch_fullname = models.CharField(max_length=255, null=False, blank=False)
    routers = models.TextField(null=False, blank=False)
    access_points = models.TextField(null=False, blank=False)
    internet_packages = models.TextField(null=False, blank=False)
    total_ap = models.IntegerField(null=False)
    sdk_user_id = models.BigIntegerField(null=False)
    app_id = models.CharField(max_length=50, null=False, blank=False)
    sdk_acc_username = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_created=True, null=True, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
