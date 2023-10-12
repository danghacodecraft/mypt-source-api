from django.db import models
from app.configs import app_settings

# Create your models here.
class OauthGrants(models.Model):
    class Meta:
        db_table = 'mypt_chm_auth_oauth_grants'

    id = models.AutoField(primary_key=True)
    grant = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)

    def findGrantIdByGrantType(self, grantType):
        grants = {
            "account_credentials_grant": app_settings.ACC_CREDENTIALS_GRANT_ID,
            "refresh_token": app_settings.REFRESH_TOKEN_GRANT_ID
        }
        if grants.get(grantType, None) is not None:
            return int(grants.get(grantType))
        else:
            return 0
