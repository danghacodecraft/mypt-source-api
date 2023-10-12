from django.db import models
from core.helpers.global_variables import *

class AccountManagement(models.Model):
    class Meta:
        db_table = MYSQL_ACCOUNT_MANAGEMENT_TB

    emp_code = models.CharField(primary_key=True, max_length=20)
    MBN_account_name = models.CharField(max_length=20)
    block_name = models.CharField(max_length=45)
    device_id = models.CharField(max_length=50)
    toa_do_van_phong = models.CharField(max_length=50)
    toa_do_kho = models.CharField(max_length=50)
    toa_do_lam_viec = models.CharField(max_length=50)
    ban_kinh_lam_viec = models.CharField(max_length=50)
    acctive_time = models.CharField(max_length=50)
    device_id_mypt = models.CharField(max_length=450)
    device_name = models.CharField(max_length=45)
    device_model = models.CharField(max_length=45)
    device_token = models.CharField(max_length=255)

    def __str__(self):
        return self.MBN_account_name
