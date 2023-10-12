from django.db import models


# Create your models here.
class SurveyEquipments(models.Model):
    LIST_MODEL_TYPE = {
        'model': 'model',
        'other': 'other'
    }
    LIST_MODEM_RULE = {
        'modem': 'Modem',
        'access_point': 'Access Point'
    }

    MODEL_TYPE_CHOICES = (
        ('model', LIST_MODEL_TYPE['model']),
        ('other', LIST_MODEL_TYPE['other'])
    )

    MODEM_RULE_CHOICES = (
        ('modem', LIST_MODEM_RULE['modem']),
        ('access_point', LIST_MODEM_RULE['access_point'])
    )

    class Meta:
        db_table = 'mypt_chm_survey_equipment'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    model_survey_id = models.BigIntegerField(null=False)
    id_equipment = models.IntegerField(null=False, default=0)
    parent_name = models.CharField(max_length=100, null=False, blank=False)
    modem_rule = models.CharField(choices=MODEM_RULE_CHOICES, max_length=50, null=False, blank=False)
    lan_wifi = models.IntegerField(null=False)
    wifi = models.IntegerField(null=False)
    wifi_24_ghz = models.IntegerField(null=True)
    wifi_5_ghz = models.IntegerField(null=True)
    quantity = models.IntegerField(null=False)
    model_type = models.CharField(choices=MODEL_TYPE_CHOICES, max_length=50, null=False, blank=False)

    def __str__(self):
        return self.parent_name
