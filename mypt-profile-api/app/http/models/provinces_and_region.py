from django.db import models


class ProvincesAndRegion(models.Model):
    class Meta:
        db_table = 'mypt_profile_provinces_and_regions'

    province_code = models.CharField(max_length=100, primary_key=True)
    province_name = models.CharField(max_length=100)
    parent_depart = models.CharField(max_length=45)
    region = models.CharField(max_length=45)
    region_code = models.CharField(max_length=45)
    created_at = models.DateTimeField()
    update_at = models.DateTimeField()
