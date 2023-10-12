from django.db import models

# Create your models here.
class UserSenders(models.Model):
    class Meta:
        db_table = 'mypt_chatbot_user_senders_v13'

    sender_id = models.CharField(max_length=255, primary_key=True)
    user_id = models.IntegerField(null=False)
    email = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_created=True,auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
