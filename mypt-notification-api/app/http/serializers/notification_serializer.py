from ..models.notification import *
from ..models.notification_topic import *
from ..models.notification_topic_group import *
from ..models.notification_config import *
from rest_framework import serializers

class NotificationSerializer(serializers.HyperlinkedModelSerializer):
	topicType = serializers.CharField(required=False, source='topic_type')
	contentShort = serializers.CharField(required=False, source='content_center_app')
	content = serializers.CharField(required=False, source='content_popup')
	contentLong = serializers.CharField(required=False, source='content_app')
	isReaded = serializers.IntegerField(required=False, source='is_readed')
	isLove = serializers.IntegerField(required=False, source='get_is_love')
	receivedAtDate = serializers.DateTimeField(required=False, source='get_received_at_date')
	receivedAtTime = serializers.DateTimeField(required=False, source='get_received_at_time')
	email = serializers.CharField(required=False)
	navigate = serializers.DictField(required=False)
	direction = serializers.CharField(required=False)	
	class Meta:
		model = Notification
		fields = ['email','id','isLove', 'navigate', 'topicType', 'title', 'contentShort', 'contentLong', 'content', 'direction', 'isReaded', 'receivedAtDate', 'receivedAtTime']


class NotificationTopicSerializer(serializers.HyperlinkedModelSerializer):
	groupAlias = serializers.CharField(source='group_alias')
	topicType = serializers.CharField(source='topic_type')
	titleNoti = serializers.CharField(source='title_noti')
	contentShort = serializers.CharField(source='content_short')
	contentLong = serializers.CharField(source='content_long')
	createAt = serializers.DateTimeField(source='created_at')
	class Meta:
		model = NotificationTopic
		fields = ['groupAlias','topicType','titleNoti','contentShort','content','contentLong','direction','createAt']
        
        
class NotificationTopicGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NotificationTopicGroup
        fields = ['alias', 'title']
	
 
class SaveNotification(serializers.ModelSerializer):
	title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	data_input = serializers.JSONField(default=None, allow_null=True) #(required=False, allow_null=True, default=None)
	email = serializers.CharField(required=False, allow_null=True)
	contentShort = serializers.CharField(required=False, source='content_center_app', allow_blank=True)
	content = serializers.CharField(required=False, source='content_popup', allow_blank=True)
	contentLong = serializers.CharField(required=False, source='content_app', allow_blank=True)
	isReaded = serializers.IntegerField(required=False, source='is_readed')
	direction = serializers.CharField(required=False)
	createdAt = serializers.DateTimeField(required=False, source='created_at', allow_null=True)
	updatedAt = serializers.DateTimeField(required=False, source='updated_at', allow_null=True)
	is_send = serializers.IntegerField(required=False)
	is_readed = serializers.IntegerField(required=False)
	process_status = serializers.CharField(required=False)
	data_action = serializers.CharField(required=False, allow_null=True)
	action_type = serializers.CharField(required=False, allow_null=True)
	popup_data_action = serializers.CharField(required=False, allow_null=True)
	popup_action_type = serializers.CharField(required=False, allow_null=True)
	receivedAt = serializers.DateTimeField(required=False, source='received_at', allow_null=True)
	send_at = serializers.DateTimeField(required=False, allow_null=True, default=None)
	sender_id = serializers.IntegerField(required=False, allow_null=True, default=None)
	receive_device_id = serializers.CharField(required=False, allow_null=True, default=None)
	receive_status = serializers.CharField(required=False, allow_null=True, default=None)
	noti_interaction = serializers.CharField(required=False, allow_null=True, default=None)
	priority = serializers.IntegerField(default=0, required=False)

	class Meta:
		model = Notification
		fields = [
			"title","email","contentShort","content",
			"contentLong","isReaded","direction",
			"receivedAt","createdAt","updatedAt","action_type",
			"is_send","is_readed","process_status","is_fake","topic_type","data_action",
			"send_at", "sender_id", "receive_device_id", "receive_status", "id",
			"noti_interaction", "popup_data_action", "popup_action_type", "data_input",
   			"priority"
		]
  
class NotificationUpdateSerializer(serializers.Serializer):
	noti_identify = serializers.DictField(required=True)
	received_at = serializers.DateTimeField(required=False, allow_null=True)
	receive_status = serializers.CharField(required=False, allow_null=True, default="app_off")
	noti_interaction = serializers.CharField(required=False, allow_null=True, default="ignore")
 
class NotificationIdentifySerializer(serializers.Serializer):
	noti_id = serializers.IntegerField(required=True, allow_null=True)
	sender_id = serializers.IntegerField(required=True, allow_null=True)
	send_at = serializers.DateTimeField(required=True, allow_null=True)
	device_id = serializers.CharField(required=True, allow_null=True)
     
class NotificationConfigsSerializer(serializers.ModelSerializer):
    config_type = serializers.CharField(required=False)
    config_key = serializers.CharField(required=True)
    config_value = serializers.CharField(required=True)
    config_description_vi = serializers.CharField(required=False)
    config_description_en = serializers.CharField(required=False)
    config_status = serializers.CharField(required=False)
    owner = serializers.CharField(required=False)
    date_created = serializers.DateTimeField(required=False)
    date_last_updated = serializers.DateTimeField(required=False)
    note = serializers.CharField(required=False)
    
    class Meta:
        model = NotificationConfigs
        fields = '__all__'
