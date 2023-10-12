from django.db import models


class SettingUserHomeTabs(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(null=False, default=0)
    tab_id = models.PositiveIntegerField(null=False, default=0)
    shown_start_date = models.DateTimeField(null=True, default=None)
    shown_end_date = models.DateTimeField(null=True, default=None)
    is_shown = models.SmallIntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mypt_setting_users_home_tabs'
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'tab_id'], name='unique_userId_tabId_mypt_setting_users_home_tabs'
            )
        ]