# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class SalaryCallApiInsideHistories(models.Model):
    api_full_url = models.CharField(max_length=250)
    api_method = models.CharField(max_length=10)
    http_status = models.SmallIntegerField()
    http_message = models.CharField(max_length=250, blank=True, null=True)
    total_time = models.FloatField(blank=True, null=True)
    request_headers = models.JSONField(blank=True, null=True)
    response_headers = models.JSONField(blank=True, null=True)
    response_status = models.IntegerField()
    response_message = models.CharField(max_length=250,  blank=True, null=True)
    response_error = models.CharField(max_length=250,  blank=True, null=True)
    year_call_api = models.SmallIntegerField()
    month_call_api = models.IntegerField()
    day_call_api = models.IntegerField()
    employee_code = models.CharField(max_length=50, blank=True, null=True)
    request_body = models.CharField(max_length=250)
    response_body = models.JSONField(blank=True, null=True)
    response_curl_info = models.JSONField(blank=True, null=True)
    date_row_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'salary_call_api_inside_histories'
