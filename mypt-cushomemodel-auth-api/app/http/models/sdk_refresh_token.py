from django.db import models

# Create your models here.
class SdkRefreshToken(models.Model):
    class Meta:
        db_table = 'mypt_chm_auth_sdk_oauth_refresh_tokens'

    id = models.CharField(max_length=50, primary_key=True)
    access_token_id = models.CharField(max_length=50)
    user_id = models.IntegerField()
    app_id = models.CharField(max_length=50, null=True)
    acc_username = models.CharField(max_length=255, null=True)
    client_id = models.CharField(max_length=50)
    code_verifier = models.CharField(max_length=128)
    revoked = models.IntegerField()
    expires_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
