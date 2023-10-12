from django.db import models
from core.helpers.global_variables import *

class SendEmail(models.Model):
    class Meta:
        db_table = MYSQL_MYPT_CHECKIN_SEND_EMAIL

    email = models.CharField(primary_key=True, max_length=255)
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()

    def __str__(self):
        return self.email