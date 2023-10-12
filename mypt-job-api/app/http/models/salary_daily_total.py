from django.db import models
from django.utils import timezone


class SalaryDailyTotal(models.Model):
    salary_daily_total_id = models.AutoField(primary_key=True)
    employee_code = models.CharField(max_length=12)
    employee_email = models.CharField(max_length=250)
    salary_total = models.IntegerField()
    salary_details = models.JSONField(default=None, blank=True, null=True)
    salary_inside_details = models.JSONField()
    year_calculate = models.IntegerField()
    month_calculate = models.IntegerField()
    day_last_calculate = models.IntegerField()
    date_last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'salary_daily_total'
