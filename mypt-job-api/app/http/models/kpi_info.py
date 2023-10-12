from django.db import models


# Create your models here.
class KpiInfo(models.Model):
    class Meta:
        db_table = 'mypt_job_kpi_info'

    id = models.IntegerField(primary_key=True)
    kpi_type = models.CharField(max_length=255)
    kpi_value = models.TextField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    year = models.IntegerField()
    target = models.FloatField(max_length=11)
    owner = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True, auto_created=True)
