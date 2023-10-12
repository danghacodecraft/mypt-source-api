from django.db import models


class SettingFunctionIcons(models.Model):
    icon_id = models.PositiveIntegerField(primary_key=True)
    ordering = models.PositiveIntegerField()
    icon_title = models.CharField(max_length=100, null=False)
    icon_url = models.JSONField(null=False)
    permission_codes = models.CharField(max_length=1000, null=False, default='')
    action_type = models.CharField(max_length=100, null=True, default=None)
    data_action = models.CharField(max_length=255, null=True, default=None)
    extra_data = models.TextField(null=True, default=None)
    is_deleted = models.SmallIntegerField(default=0)
    function_status = models.CharField(max_length=50, default="WORKING")
    group_type = models.CharField(max_length=50, default="")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    theme_id = models.IntegerField(null=True, default=None)
    on_home = models.BooleanField(default=False)

    class Meta:
        db_table = 'mypt_setting_function_icons'
