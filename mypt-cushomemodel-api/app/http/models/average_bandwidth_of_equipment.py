from django.db import models


# Create your models here.
class AverageBandwidthOfEquipment(models.Model):
    class Meta:
        db_table = 'mypt_chm_average_bandwidth_of_equipment'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    average_bandwidth = models.FloatField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True,null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=False)
    is_active = models.IntegerField(null=False, blank=False)
    mypt_user_id = models.BigIntegerField(null=True, blank=True)
    mypt_user_email = models.CharField(max_length=255, null=True, blank=True)
    mypt_user_fullname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
