# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class SalaryMonthly(models.Model):
    salary_monthly_id = models.AutoField(primary_key=True)
    employee_code = models.CharField(max_length=12)
    employee_email = models.CharField(max_length=250)
    salary_total = models.IntegerField()
    salary_details = models.JSONField(default=None, blank=True, null=True)
    salary_inside_details = models.JSONField()
    year_calculate = models.IntegerField()
    month_calculate = models.IntegerField()
    date_row_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'salary_monthly'
