from django.db import models


# Create your models here.
class BuildHouseModel(models.Model):

    class Meta:
        db_table = 'mypt_chm_build_house_model'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    model_survey_id = models.IntegerField(null=False)
    house_floor = models.IntegerField(null=False)
    house_width = models.FloatField(null=False)
    house_length = models.FloatField(null=False)
    tx_location = models.TextField(null=True, blank=False)
    tx_power = models.TextField(null=True, blank=False)
    tx_name = models.TextField(null=True, blank=False)
    wall_attenuation = models.IntegerField(null=True)
    wall_attenuation_info = models.TextField(null=True, blank=False)
    image_shape = models.TextField(null=False, blank=False)
    corners = models.TextField(null=False, blank=False)
    edges = models.TextField(null=False, blank=False)
    image_link_original = models.CharField(max_length=255, null=False, blank=False)
    image_link_wifi24 = models.CharField(max_length=255, null=True, blank=False)
    image_link_wifi5 = models.CharField(max_length=255, null=True, blank=False)
    status_updated = models.IntegerField(null=False, default=0)
    image_type = models.CharField(max_length=50, null=False, blank=False)
    size = models.CharField(max_length=100, null=False, blank=False)
    sketches = models.TextField(null=True, blank=False)
    devices = models.TextField(null=True, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
