from django.db import models


class AgencyAndProvince(models.Model):
    class Meta:
        db_table = 'mypt_profile_agency_and_province'

    agency = models.CharField(max_length=45, primary_key=True)
    province = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    update_at = models.DateTimeField()
