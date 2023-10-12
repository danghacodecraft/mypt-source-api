from django.db import models


class CheckinLocation(models.Model):
    class Meta:
        db_table = 'mypt_profile_checkin_location'

    building_office_id = models.CharField(max_length=30, unique=True, primary_key=True)
    building_office_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    status_working = models.IntegerField()
