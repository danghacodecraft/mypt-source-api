from django.db import models
from ...core.helpers.global_variables import *

class ResponseContent(models.Model):
    class Meta:
        db_table = MYSQL_MYPT_RESPONSE_CONTENT

    id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=450)
    def __str__(self):
        return self.id