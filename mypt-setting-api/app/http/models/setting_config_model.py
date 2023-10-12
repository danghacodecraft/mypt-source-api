from django.db import models


class SettingConfig(models.Model):
    class Meta:
        db_table = 'mypt_setting_configs'

    config_id = models.BigAutoField(primary_key=True)
    config_type = models.CharField(max_length=20, unique=True)
    config_key = models.CharField(max_length=100)
    config_value = models.TextField()
    config_description_vi = models.TextField()
    config_description_en = models.TextField()
    config_status = models.CharField(max_length=20, unique=True, default="enabled")
    owner = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    note = models.CharField(max_length=255)
