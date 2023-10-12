from django.db import models


class IqcConfig(models.Model):
    class Meta:
        db_table = "mypt_iqc_configs"

    config_key = models.CharField(primary_key=True, max_length=20)
    config_value = models.JSONField()
    note = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.config_key
