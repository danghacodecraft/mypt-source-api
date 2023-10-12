from django.db import models

# Create your models here.
class NotificationTopic(models.Model):
    
    # class processStatus(models.TextChoices):
    #     UNPUB = 'unpublish'
    #     PUB = 'publish'
    #     DEL = 'deleted'

    class Meta:
        db_table = 'mypt_notification_topics'
  
    group_alias  = models.CharField(max_length=250)
    topic_type = models.CharField(max_length=250)
    title_noti = models.CharField(max_length=250)
    content_short = models.TextField()
    content = models.TextField()
    content_long = models.TextField()
    direction = models.CharField(max_length=250)
    url = models.CharField(max_length=250)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField()
    # process_status = models.CharField(
    #     max_length=3,
    #     choices=processStatus.choices,
    #     default=processStatus.PUB,
    # )