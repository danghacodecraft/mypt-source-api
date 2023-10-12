from django.db import models

# Create your models here.
class SdkAccessToken(models.Model):
    class Meta:
        db_table = 'mypt_chm_auth_sdk_oauth_access_tokens'

    id = models.CharField(max_length=50, primary_key=True)
    user_id = models.IntegerField()
    app_id = models.CharField(max_length=50, null=True)
    acc_username = models.CharField(max_length=255, null=True)
    client_id = models.CharField(max_length=50)
    code_verifier = models.CharField(max_length=128)
    auth_code_id = models.CharField(max_length=50)
    refresh_token_id = models.CharField(max_length=50)
    grant_id = models.IntegerField()
    login_to_sdk = models.IntegerField()
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    device_token = models.CharField(max_length=255)
    device_platform = models.CharField(max_length=50)
    revoked = models.IntegerField()
    expires_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now_add=True)
