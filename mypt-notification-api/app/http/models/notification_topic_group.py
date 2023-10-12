from django.db import models

# Create your models here.
class NotificationTopicGroup(models.Model):

    class Meta:
        db_table = 'mypt_notification_topics_group'

    id = models.AutoField(primary_key=True)    
    alias  = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    process_status = models.CharField(max_length=250)        
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField()