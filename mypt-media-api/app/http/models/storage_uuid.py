from django.db import models
from app.core.helpers.global_variables import *



class StorageUuid(models.Model):
    class Meta:
        db_table = MYSQL_STORAGE_UUID_DATA_TB

    uuid = models.CharField(primary_key=True, max_length=50)
    link_data = models.CharField(max_length=200)
    email = models.CharField(max_length=45)
    update_time = models.DateTimeField()
    link_local = models.CharField(max_length=200)
    folder = models.CharField(max_length=45)
    child_folder = models.CharField(max_length=45)

    def __str__(self):
        return self.uuid