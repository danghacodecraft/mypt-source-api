from django.db import models

class ThemeManager(models.Model):
    class Meta:
        db_table = 'mypt_setting_event_theme'
        
    id = models.AutoField(primary_key=True)
    theme_code = models.CharField(max_length=100)
    icon_app = models.CharField(max_length=50)
    theme_background = models.CharField(max_length=1000, null=True, default=None)
    branch = models.CharField(max_length=4, default="ALL")
    start_date = models.DateTimeField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)