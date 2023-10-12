from django.db import models


# Create your models here.
class TemplateGroups(models.Model):
    class Meta:
        db_table = 'mypt_chm_template_groups'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
    mypt_user_id = models.BigIntegerField(null=True, blank=True)
    mypt_user_email = models.CharField(max_length=255, null=True, blank=True)
    mypt_user_fullname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
