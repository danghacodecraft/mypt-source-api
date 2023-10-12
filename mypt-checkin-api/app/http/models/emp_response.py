from django.db import models
from ...core.helpers.global_variables import *



class EmpResponse(models.Model):
    class Meta:
        db_table = MYSQL_MYPT_CHECKIN_EMP_RESPONSE

    id = models.IntegerField(primary_key=True)
    emp_code = models.CharField(max_length=45)
    update_time = models.DateTimeField()
    response = models.TextField()
    response_id = models.IntegerField()
    coordinate = models.CharField(max_length=500)
    checkin_id = models.IntegerField()
    device_id = models.CharField(max_length=500)

    def __str__(self):
        return self.emp_code

    def get_update_time_format(self):
        if self.update_time:
            datatime = self.update_time
            datetimeresult = str(datatime.strftime(DATETIME_FORMAT_EXPORT))
            return datetimeresult
        return ''