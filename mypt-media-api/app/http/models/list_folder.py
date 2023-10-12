from django.db import models
from app.core.helpers.global_variables import *



class ListFolder(models.Model):
    class Meta:
        db_table = MYSQL_MYPT_MEDIA_LIST_FOLDER
    folder = models.CharField(primary_key=True, max_length=255)
    date_create = models.DateTimeField()

    def __str__(self):
        return self.folder