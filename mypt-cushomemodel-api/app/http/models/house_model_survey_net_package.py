from django.db import models


# Create your models here.
class SurveyNetPackage(models.Model):
    LIST_MODEL_TYPE = {
        'model': 'model',
        'other': 'other'
    }

    MODEL_TYPE_CHOICES = (
        ('model', LIST_MODEL_TYPE['model']),
        ('other', LIST_MODEL_TYPE['other'])
    )

    class Meta:
        db_table = 'mypt_chm_survey_net_package'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    model_survey_id = models.BigIntegerField(null=False)
    id_package = models.IntegerField(null=False, default=0)
    name = models.CharField(max_length=100, null=False, blank=False)
    download_speed = models.IntegerField(null=False)
    upload_speed = models.IntegerField(null=False)
    quantity = models.IntegerField(null=False)
    model_type = models.CharField(choices=MODEL_TYPE_CHOICES, max_length=50, null=False, blank=False)
