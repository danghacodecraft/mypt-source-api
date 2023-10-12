from django.db import models


# Create your models here.
class HouseModelSurvey(models.Model):
    GUARANTEE = 'guarantee'
    NOT_GUARANTEE = 'not_guarantee'
    LACK_OF_INFORMATION = 'lack_of_information'
    LIST_STATUS_SURVEY = {
        GUARANTEE: 'Đảm bảo',
        NOT_GUARANTEE: 'Không đảm bảo',
        LACK_OF_INFORMATION: 'Thiếu thông tin'
    }

    STATUS_SURVEY_CHOICES = (
        (GUARANTEE, LIST_STATUS_SURVEY[GUARANTEE]),
        (NOT_GUARANTEE, LIST_STATUS_SURVEY[NOT_GUARANTEE]),
        (LACK_OF_INFORMATION, LIST_STATUS_SURVEY[LACK_OF_INFORMATION]),
    )

    class Meta:
        db_table = 'mypt_chm_house_model_survey'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    contract_code = models.CharField(max_length=100)
    regions = models.CharField(max_length=255)
    branch_fullname = models.CharField(max_length=255)
    sdk_user_id = models.BigIntegerField(null=False, blank=False)
    app_id = models.CharField(max_length=50, null=False, blank=False)
    sdk_acc_username = models.CharField(max_length=255, null=True, blank=False)
    id_type = models.IntegerField(null=False, blank=False)
    model_type = models.CharField(max_length=255, null=False, blank=False)
    customer_type = models.CharField(max_length=255, null=False, blank=False)
    house_length = models.FloatField(null=False, blank=False)
    house_width = models.FloatField(null=False, blank=False)
    floors = models.IntegerField(null=False, blank=False)
    rows_per_floor = models.IntegerField(null=True, blank=False)
    rooms_per_row = models.IntegerField(null=True, blank=False)
    people_per_room = models.IntegerField(null=True, blank=False)
    user_wifi = models.IntegerField(null=False, blank=False)
    user_lan = models.IntegerField(null=False, blank=False)
    user_camera = models.IntegerField(null=False, blank=False)
    lux_package_check = models.IntegerField(null=False, blank=False)
    upload_alot_check = models.IntegerField(null=False, blank=False)
    concurrent_usage_rate = models.IntegerField(null=False, blank=False)
    other_check = models.IntegerField(null=False, blank=False)
    other_width = models.FloatField(null=True, blank=False)
    other_length = models.FloatField(null=True, blank=False)
    other_user_wifi = models.IntegerField(null=True, blank=False)
    internet_packages = models.TextField()
    routers = models.TextField()
    access_points = models.TextField()
    total_ap = models.TextField()
    conclusion = models.TextField()
    status_survey = models.CharField(max_length=50, choices=STATUS_SURVEY_CHOICES)
    reason = models.CharField(max_length=1000)
    is_current = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField()
