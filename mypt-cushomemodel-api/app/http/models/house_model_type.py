from django.db import models


# Create your models here.
class HouseModelType(models.Model):
    """
    model_type:
    1 - main
    2 - extra
    """
    MAIN = 1
    EXTRA = 2

    CHOICES = (
        (MAIN, 'Main'),
        (EXTRA, 'Extra')
    )

    class Meta:
        db_table = 'mypt_chm_house_model_type'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    model_type = models.IntegerField(choices=CHOICES, default=MAIN, null=False, blank=False)
    covered_area = models.IntegerField(null=False, blank=False)
    group_template = models.CharField(null=False, blank=False, max_length=20)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
    is_active = models.IntegerField(null=False, blank=False)
    mypt_user_id = models.BigIntegerField(null=True, blank=True)
    mypt_user_email = models.CharField(max_length=255, null=True, blank=True)
    mypt_user_fullname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
