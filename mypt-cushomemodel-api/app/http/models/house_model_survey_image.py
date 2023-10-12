from django.db import models


# Create your models here.
class HouseModelSurveyImage(models.Model):
    LIST_SKETCHES_TYPE = {
        'app': 'Ảnh vẽ trên ứng dụng',
        'paper': 'Ảnh vẽ trên giấy'
    }

    SKETCHES_TYPE_CHOICES = (
        ('app', 'app'),
        ('paper', 'paper'),
    )

    class Meta:
        db_table = 'mypt_chm_house_model_survey_image'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    model_survey_id = models.BigIntegerField(null=False)
    house_floor = models.IntegerField(null=False, blank=False)
    house_size = models.CharField(max_length=100, null=False, blank=False)
    tx_devices_info = models.TextField(null=False, blank=False)
    sketches = models.TextField(null=False, blank=False)
    sketches_type = models.CharField(max_length=20, choices=SKETCHES_TYPE_CHOICES, null=False, blank=False)
    status_updated = models.IntegerField(null=False)
    sdk_user_id = models.BigIntegerField(null=False, blank=False)
    app_id = models.CharField(max_length=50, null=False, blank=False)
    sdk_acc_username = models.CharField(max_length=255, null=True, blank=False)
    created_at = models.DateTimeField(null=False)
