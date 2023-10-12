from django.db import models
from core.helpers.global_variables import *

from core.helpers.utils import *

class EmpCheckin(models.Model):
    class Meta:
        db_table = MYSQL_EMP_CHECKIN_TB

    checkin_id = models.IntegerField(primary_key=True)
    MBN_account_name = models.CharField(max_length=30)
    emp_code = models.CharField(max_length=20)
    checkin_date = models.DateField()
    checkin_time = models.CharField(max_length=20)
    checkin_day = models.CharField(max_length=20)
    checkin_month = models.CharField(max_length=20)
    checkin_year = models.CharField(max_length=20)
    sheet_time = models.CharField(max_length=20)
    workday_factor = models.FloatField()
    workday_convert = models.FloatField()
    block_name = models.CharField(max_length=20)
    checkin_success = models.CharField(max_length=20)
    location = models.CharField(max_length=20)
    team_name = models.CharField(max_length=20)
    note = models.CharField(max_length=20)
    close_case = models.IntegerField()
    coordinate_office = models.CharField(max_length=100)
    coordinate_block = models.CharField(max_length=100)
    block_distance = models.FloatField()
    count_auto = models.IntegerField()
    count_response = models.IntegerField()
    confirm = models.IntegerField()
    history_coordinate = models.TextField()
    device_name = models.CharField(max_length=255)
    # too_late = models.IntegerField()



    def __str__(self):
        return self.MBN_account_name

    # def get_t_assigned_format(self):
    #     if self.t_assigned:
    #         datatime = self.t_assigned
    #         datetimeresult = str(datatime.strftime(DATETIME_FORMAT_EXPORT))
    #         return datetimeresult
    #     return None

    def get_checkin_date_format(self):
        if self.checkin_date:
            datatime = self.checkin_date
            datetimeresult = str(datatime.strftime(DATE_FORMAT_EXPORT))
            return datetimeresult
        return None

    def get_device_name_format(self):
        if is_null_or_empty(self.device_name):
            return ""
        return self.device_name




    # def get_device_name_format(self):
    #     if is_null_or_empty(self.device_name):
    #         return ""
    #     return self.device_name

