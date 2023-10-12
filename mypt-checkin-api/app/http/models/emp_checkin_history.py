from django.db import models
from core.helpers.global_variables import *



class empCheckinHistory(models.Model):
    class Meta:
        db_table = MYSQL_MYPT_CHECKIN_EMP_CHECKIN_HISTORY

    history_id = models.IntegerField(primary_key=True)
    checkin_id = models.IntegerField()
    coordinate = models.CharField(max_length=30)
    update_time = models.DateTimeField()
    status = models.IntegerField()
    type_checkin = models.CharField(max_length=45)
    emp_code = models.CharField(max_length=45)
    checkin_date = models.DateField()



    def __str__(self):
        return self.history_id