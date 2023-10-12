from django.db import models


class SettingHomeTabs(models.Model):
    tab_id = models.PositiveIntegerField(primary_key=True)
    tab_name = models.CharField(max_length=100, null=False)
    tab_code = models.CharField(max_length=100, null=False, unique=True)
    permission_codes = models.CharField(max_length=1000, null=False, default='')
    app_version = models.CharField(max_length=50, null=False, default="1.0")
    is_default = models.SmallIntegerField(default=1)
    is_deleted = models.SmallIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mypt_setting_home_tabs'
