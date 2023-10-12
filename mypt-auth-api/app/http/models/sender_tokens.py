from django.db import models

# Create your models here.
class SenderTokens(models.Model):
    class Meta:
        db_table = 'mypt_chatbot_sender_tokens_v13'

    sender_token = models.CharField(max_length=255, primary_key=True)
    sender_id = models.CharField(max_length=255)
    user_id = models.IntegerField(null=False)
    is_deleted = models.IntegerField(null=False)
    date_created = models.DateTimeField(auto_created=True, auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
