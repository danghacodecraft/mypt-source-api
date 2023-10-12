from django.db import models
from django.utils import timezone


class SalaryReal(models.Model):
    luong_hoach_toan_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    month = models.CharField(max_length=20, blank=True, null=True)
    luong_thang = models.CharField(max_length=100, blank=True, null=True)
    luong_thu_viec = models.CharField(max_length=100, blank=True, null=True)
    luong_dao_tao_nghe = models.CharField(max_length=100, blank=True, null=True)
    luong_cong_thuc = models.CharField(max_length=100, blank=True, null=True)
    luong_dong_bhxh = models.CharField(max_length=100, blank=True, null=True)
    bhyt = models.CharField(max_length=100, blank=True, null=True)
    bhxh = models.CharField(max_length=100, blank=True, null=True)
    bhtn = models.CharField(max_length=100, blank=True, null=True)
    kinh_phi_cd = models.CharField(max_length=100, blank=True, null=True)
    giam_tru_gia_canh = models.CharField(max_length=100, blank=True, null=True)
    sl_nguoi_phu_thuoc = models.CharField(max_length=100, blank=True, null=True)
    muc_giam_tru_npt = models.CharField(max_length=100, blank=True, null=True)
    thue_thu_nhap_ca_nhan = models.CharField(max_length=100, blank=True, null=True)
    bu_tru_khac_sau_thue = models.CharField(max_length=100, blank=True, null=True)
    truy_thu_hoan_thue_tncn = models.CharField(db_column='truy_thu_hoan_thue_TNCN', max_length=100, blank=True,
                                               null=True)  # Field name made lowercase.
    truy_thu_bhyt = models.CharField(db_column='truy_thu_BHYT', max_length=100, blank=True,
                                     null=True)  # Field name made lowercase.
    tam_ung = models.CharField(max_length=100, blank=True, null=True)
    hoan_ung = models.CharField(max_length=100, blank=True, null=True)
    luong_thuc_nhan = models.CharField(max_length=100, blank=True, null=True)
    hinh_thuc_chi_tra = models.CharField(max_length=100, blank=True, null=True)
    update_time = models.CharField(max_length=50, blank=True, null=True)
    update_by = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        # abstract = True
        db_table = 'luong_hoach_toan_tb'
