from django.db import models


class SalaryRealTime(models.Model):
    class Meta:
        db_table = 'luong_realtime_tb'

    emp_code = models.CharField(max_length=50, primary_key=True)
    SumSalaryMonth = models.CharField(max_length=50)
    daily = models.DateField()

    def __str__(self):
        return self.emp_code
