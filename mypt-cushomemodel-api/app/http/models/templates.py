from django.db import models


# Create your models here.
class Templates(models.Model):
    class Meta:
        db_table = 'mypt_chm_templates'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    group_id = models.IntegerField(null=False)
    sketches = models.TextField(null=True, blank=True)
    sketches_type = models.TextField(null=True, blank=True, default='app')
    image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
    mypt_user_id = models.BigIntegerField(null=True, blank=True)
    mypt_user_email = models.CharField(max_length=255, null=True, blank=True)
    mypt_user_fullname = models.CharField(max_length=255, null=True, blank=True)

    # def __str__(self):
    #     return self.name
