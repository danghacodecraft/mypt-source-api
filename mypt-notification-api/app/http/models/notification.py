from email.policy import default
from django.db import models
from dateutil.parser import parse
from datetime import datetime

# Create your models here.
class Notification(models.Model):
    class processStatus(models.TextChoices):
        UNPUB = 'unpublish'
        PUB = 'publish'
        DEL = 'deleted' 

    class Meta:
        db_table = 'mypt_notifications'

    id = models.AutoField(primary_key=True)    
    topic_type = models.CharField(max_length=100, default="noti_base")    
    email = models.CharField(max_length=100)    
    user_id  = models.IntegerField()
    gateway_id = models.CharField(max_length=250)
    title = models.CharField(max_length=255, blank=True)
    content_center_app = models.TextField()
    content_app = models.TextField()
    content_popup = models.TextField()
    direction = models.CharField(max_length=255, default="popup")
    data_action = models.CharField(max_length=255)
    action_type = models.CharField(max_length=255)
    popup_action_type = models.CharField(max_length=255)
    popup_data_action = models.CharField(max_length=255)
    is_send = models.IntegerField(default=1)
    is_readed = models.IntegerField()
    is_fake = models.IntegerField(default=0)
    result_call_api = models.TextField()    
    data_input = models.JSONField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)
    love = models.DateTimeField()
    pin = models.DateTimeField()
    process_status = models.CharField(max_length=250)
    process_status = models.CharField(
        max_length=255,
        choices=processStatus.choices,
        default=processStatus.PUB,
    )
    
    received_at = models.DateTimeField(null=True, default=None)
    send_at = models.DateTimeField(null=True, default=None)
    sender_id = models.IntegerField(null=True, default=None)
    receive_device_id = models.TextField(null=True, default=None)
    receive_status = models.TextField(null=True, default=None)
    noti_interaction = models.CharField(max_length=255, null=True, default=None)
    priority = models.IntegerField(default=0)
    
    def navigate(self):
        try:
            return {
                "dataAction":  self.action_data(),
                "actionType": self.action()
            }
        except:
            return {
                "dataAction":  "",
                "actionType": ""
            }
            
    def action_data(self):
        if self.data_action is None:
            return ""
        return self.data_action
    
    def action(self):
        if self.action_type is None:
            return ""
        return self.action_type


    def get_received_at_date(self):
        if self.received_at:
            datatime = self.received_at
            timeresult = str(datatime.strftime("%d-%m-%Y"))
            return timeresult
        else:
            None
    def get_received_at_time(self):
        if self.received_at:
            datatime = self.received_at
            timeresult = str(datatime.strftime("%H:%M"))
            return timeresult
        else:
            None
            
    def get_is_love(self):
        if self.love is None:
            return 0
        return 1


    # class ProcessStatus(models.TextChoices):        
    #     # PUB = 'pub', _('publish')
    #     # UNPUB = 'unpub', _('unpublish')
    #     # DEL = 'del', _('deleted')
    #     unpublish = 1
    #     publish = 2
    #     unpublish = 3

    # process_status = models.CharField(
    #     max_length=2,
    #     choices=ProcessStatus.choices,
    #     default=ProcessStatus.UNPUB,
    # )
