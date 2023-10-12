from django.db import models


class SafeCard(models.Model):
    class Meta:
        db_table = "tool_ATLD_tb"

    atld_id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=30)
    nhom_dao_tao = models.CharField(max_length=100)
    so_the_ATLD = models.CharField(max_length=45)
    cap_the_chung_chi = models.CharField(max_length=100)
    ngay_cap_the_ATLD = models.DateField()
    ngay_het_han_ATLD = models.DateField()
    ngay_bat_dau_dao_tao = models.DateField()
    ngay_ket_thuc_dao_tao = models.DateField()
    tinh_trang_the_chung_chi = models.CharField(max_length=100)
    hinh_anh_the_chung_nhan = models.CharField(max_length=100)
    update_time_atld = models.DateTimeField()
    update_by = models.CharField(max_length=50)
