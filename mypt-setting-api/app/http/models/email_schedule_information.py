from django.db import models

class EmailScheduleInformation(models.Model):
    class Meta:
        db_table = 'mypt_setting_email_schedule_information'
        
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default="")
    input_data = models.TextField(null=False, blank=False)
    is_done = models.BooleanField(default=False)
