from django.db import models


# Create your models here.
class RSAKey(models.Model):
    class Meta:
        db_table = 'mypt_chm_auth_sdk_apps'

    id = models.BigAutoField(primary_key=True)
    app_id = models.CharField(max_length=50, unique=True)
    public_key = models.TextField()
    private_key = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField()

    def __str__(self):
        return self.app_id
