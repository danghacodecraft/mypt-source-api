from django.db import models


# Create your models here.
class InternetPackages(models.Model):
    """
    customer_type:
    0 - None
    1 - Cá nhân
    2 - Doanh nghiệp
    """
    CUSTOMER_TYPE_NONE = ''
    CUSTOMER_TYPE_CA_NHAN = 'ca_nhan'
    CUSTOMER_TYPE_DOANH_NGHIEP = 'doanh_nghiep'
    CUSTOMER_TYPE_TAT_CA = 'all'

    IS_AVAILABILITY = 1
    IS_NOT_AVAILABILITY = 0

    CUSTOMER_TYPE_CHOICES = (
        (CUSTOMER_TYPE_NONE, ''),
        (CUSTOMER_TYPE_CA_NHAN, 'cá nhân'),
        (CUSTOMER_TYPE_DOANH_NGHIEP, 'doanh nghiệp'),
        (CUSTOMER_TYPE_TAT_CA, 'tất cả')
    )
    customer_type_STATUS = (
        (IS_AVAILABILITY, 'được khuyến nghị'),
        (IS_NOT_AVAILABILITY, 'chưa đủ điều kiện'),
    )

    class Meta:
        db_table = 'mypt_chm_internet_packages'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    customer_type = models.CharField(max_length=100, choices=CUSTOMER_TYPE_CHOICES, default=CUSTOMER_TYPE_NONE,
                                     null=False, blank=False)
    lux = models.IntegerField(default=0)
    download_speed = models.IntegerField(null=False, blank=False)
    upload_speed = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
    is_active = models.IntegerField(choices=customer_type_STATUS, default=IS_NOT_AVAILABILITY, null=False, blank=False)
    mypt_user_id = models.BigIntegerField(null=True, blank=True)
    mypt_user_email = models.CharField(max_length=255, null=True, blank=True)
    mypt_user_fullname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
